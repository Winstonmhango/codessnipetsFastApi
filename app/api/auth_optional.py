from typing import Optional

from fastapi import Depends, Request
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from starlette.status import HTTP_401_UNAUTHORIZED

from app.api.deps import get_current_user, get_db
from app.models import User


class OAuth2PasswordBearerOptional(OAuth2):
    """
    OAuth2 password bearer scheme that allows optional authentication.
    Similar to OAuth2PasswordBearer but doesn't raise an exception if token is missing.
    """
    def __init__(
        self,
        tokenUrl: str,
        scheme_name: Optional[str] = None,
        scopes: Optional[dict] = None,
        auto_error: bool = False,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        authorization: str = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            return None
        return param


# Create an instance of the optional OAuth2 scheme
oauth2_scheme_optional = OAuth2PasswordBearerOptional(
    tokenUrl="/api/v1/auth/login",
    auto_error=False
)


def get_current_user_optional(
    request: Request,
    db = Depends(get_db),
) -> Optional[User]:
    """
    Get the current user if authenticated, otherwise return None.
    This is useful for endpoints that can be accessed both by authenticated and anonymous users.
    """
    authorization: str = request.headers.get("Authorization")
    if not authorization:
        return None
        
    scheme, token = get_authorization_scheme_param(authorization)
    if not token or scheme.lower() != "bearer":
        return None
        
    try:
        # Reuse the existing get_current_user function
        # We need to create a modified request with the token
        # This is a bit of a hack, but it works
        return get_current_user(db=db, token=token)
    except Exception:
        # Any exception means authentication failed, but we don't want to raise an error
        return None
