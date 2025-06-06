from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.services.facebook_service import FacebookService
from app.schemas.facebook import FacebookConnectRequest, FacebookConnectResponse, FacebookPageResponse, FacebookAuthResponse, FacebookConnectionResponse
from app.models.facebook_page import FacebookPage
from app.models.user import User
import secrets
import time

router = APIRouter(prefix="/facebook", tags=["facebook"])

@router.get("/auth", response_model=FacebookAuthResponse)
async def get_facebook_auth_url(
    redirect_uri: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get Facebook OAuth URL for connecting a page.
    The frontend should redirect the user to this URL for Facebook login.
    """
    # Generate a random state to prevent CSRF
    state = secrets.token_urlsafe(32)
    
    # Generate the OAuth URL
    auth_url = FacebookService.get_oauth_url(redirect_uri, state)
    
    return FacebookAuthResponse(auth_url=auth_url)

@router.post("/connect", response_model=FacebookConnectResponse)
async def connect_facebook_page(
    request: FacebookConnectRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # Exchange code for access token
        print("started...")
        token_info = FacebookService.get_access_token(request.code, request.redirect_uri)
        access_token = token_info["access_token"]
        print("access_token", access_token)
        # Exchange for long-lived token
        long_lived_token_info = FacebookService.get_long_lived_token(access_token)
        long_lived_token = long_lived_token_info["access_token"]
        print("long_lived_token", long_lived_token)
        # Get page information
        pages_info = FacebookService.get_page_access_token(long_lived_token)
        print("pages_info", pages_info)
        if not pages_info.get("data"):
            raise HTTPException(status_code=400, detail="No Facebook pages found")
        
        # Use the first page for now (can be modified to handle multiple pages)
        page = pages_info["data"][0]
        print("first page", page)
        # Check if page is already connected
        existing_page = db.query(FacebookPage).filter(
            FacebookPage.id == page["id"],
            FacebookPage.user_id == current_user.id
        ).first()
        print("existing_page", existing_page)
        if existing_page:
            if existing_page.is_active:
                return FacebookConnectResponse(
                    success=True,
                    message="Page already connected"
                )
            existing_page.is_active = True
            existing_page.access_token = page["access_token"]
            db.commit()
            return FacebookConnectResponse(
                success=True,
                page=FacebookPageResponse.from_orm(existing_page),
                message="Page reconnected successfully"
            )
        
        # Create new page connection
        new_page = FacebookPage(
            id=page["id"],
            user_id=current_user.id,
            name=page["name"],
            access_token=page["access_token"],
            picture_url=page.get("picture", {}).get("data", {}).get("url"),
            is_active=True
        )
        
        db.add(new_page)
        db.commit()
        db.refresh(new_page)
        
        return FacebookConnectResponse(
            success=True,
            page=FacebookPageResponse.from_orm(new_page),
            message="Page connected successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/disconnect/{page_id}", response_model=FacebookConnectResponse)
async def disconnect_facebook_page(
    page_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    page = db.query(FacebookPage).filter(
        FacebookPage.id == page_id,
        FacebookPage.user_id == current_user.id,
        FacebookPage.is_active == True
    ).first()
    
    if not page:
        raise HTTPException(status_code=404, detail="Facebook page not found or already disconnected")
    
    # Revoke access token
    if FacebookService.disconnect_page(page.id, page.access_token):
        page.is_active = False
        db.commit()
        return FacebookConnectResponse(
            success=True,
            message="Page disconnected successfully"
        )
    
    raise HTTPException(status_code=400, detail="Failed to disconnect page")

@router.get("/connection", response_model=FacebookConnectionResponse)
async def get_facebook_connection(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the user's Facebook page connection status.
    Returns connected=1 if an active connection exists, connected=0 otherwise.
    Includes a timestamp for client-side caching.
    """
    # Query for the most recent active Facebook page
    active_page = db.query(FacebookPage).filter(
        FacebookPage.user_id == current_user.id,
        FacebookPage.is_active == True
    ).order_by(FacebookPage.id.desc()).first()
    
    return FacebookConnectionResponse(
        connected=1 if active_page else 0,
        page=active_page,
        last_checked=time.time()
    ) 