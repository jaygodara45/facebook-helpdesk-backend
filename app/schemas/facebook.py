from pydantic import BaseModel

class FacebookAuthResponse(BaseModel):
    auth_url: str

class FacebookConnectRequest(BaseModel):
    code: str
    redirect_uri: str

class FacebookPageResponse(BaseModel):
    id: str
    name: str
    picture_url: str | None = None
    is_active: bool

    class Config:
        from_attributes = True

class FacebookConnectResponse(BaseModel):
    success: bool
    page: FacebookPageResponse | None = None
    message: str

class FacebookConnectionResponse(BaseModel):
    connected: int
    page: FacebookPageResponse | None = None
    last_checked: float  # Unix timestamp

    class Config:
        from_attributes = True 