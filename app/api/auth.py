from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse

from app.model.user import User
from app.service.authentication import (
    jwt_extract_object,
    user_htmx_dep,
)


router = APIRouter(default_response_class=JSONResponse)

# -------------------------------------------------------------
#       Endpoints
# -------------------------------------------------------------


@router.get("/", name="auth_endpoint")
def get_auth_endpoint():

    return None


@router.get(
    "/token-check", name="auth_token_check_endpoint", response_class=JSONResponse
)
def get_auth_token_refresh(
    request: Request, current_user: User = Depends(user_htmx_dep)
):

    bearer_token = request.cookies.get("access_token")  # Includes Bearer ...

    if not bearer_token:
        raise HTTPException(status_code=401, detail="Incorect token provided.")

    token_value = bearer_token.split(" ")[1]  # Extracts token string from Bearer ...
    jwt_data = jwt_extract_object(token=token_value)

    return JSONResponse(content=jwt_data, status_code=200)
