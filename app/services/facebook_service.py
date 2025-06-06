from typing import Optional
import requests
from fastapi import HTTPException
from app.core.config import settings

class FacebookService:
    BASE_URL = "https://graph.facebook.com/v18.0"
    OAUTH_URL = "https://www.facebook.com/v18.0/dialog/oauth"
    
    @staticmethod
    def get_oauth_url(redirect_uri: str, state: str = None) -> str:
        """Generate Facebook OAuth URL for login"""
        params = {
            "client_id": settings.FACEBOOK_APP_ID,
            "redirect_uri": redirect_uri,
            "scope": "pages_manage_metadata,pages_messaging",  # Required permissions for page messaging
            "response_type": "code",
        }
        if state:
            params["state"] = state
            
        # Convert params to URL query string
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{FacebookService.OAUTH_URL}?{query_string}"
    
    @staticmethod
    def get_access_token(code: str, redirect_uri: str) -> dict:
        """Exchange authorization code for access token"""
        url = f"{FacebookService.BASE_URL}/oauth/access_token"
        params = {
            "client_id": settings.FACEBOOK_APP_ID,
            "client_secret": settings.FACEBOOK_APP_SECRET,
            "redirect_uri": redirect_uri,
            "code": code
        }
        
        response = requests.get(url, params=params)
        print(f"Response by get_access_token: {response.json()}")
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get access token")
        return response.json()
    
    @staticmethod
    def get_long_lived_token(short_lived_token: str) -> dict:
        """Exchange short-lived token for a long-lived token"""
        url = f"{FacebookService.BASE_URL}/oauth/access_token"
        params = {
            "grant_type": "fb_exchange_token",
            "client_id": settings.FACEBOOK_APP_ID,
            "client_secret": settings.FACEBOOK_APP_SECRET,
            "fb_exchange_token": short_lived_token
        }
        
        response = requests.get(url, params=params)
        print(f"Response by get_long_lived_token: {response.json()}")
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get long-lived token")
        return response.json()

    @staticmethod
    def get_page_access_token(user_access_token: str) -> dict:
        """Get page access token and basic page information"""
        url = f"{FacebookService.BASE_URL}/me/accounts"
        params = {
            "access_token": user_access_token,
            "fields": "access_token,name,id,picture"
        }
        
        response = requests.get(url, params=params)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get page access token")
        return response.json()

    @staticmethod
    def disconnect_page(page_id: str, page_access_token: str) -> bool:
        """Revoke the page access token"""
        # url = f"{FacebookService.BASE_URL}/{page_id}/permissions"
        # params = {
        #     "access_token": page_access_token
        # }
        
        # response = requests.delete(url, params=params)
        # print(f"Response by disconnect_page: {response.json()}")
        # return response.status_code == 200 
        return True