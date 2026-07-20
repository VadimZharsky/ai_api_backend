from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response

from app.dependencies import get_auth_service
from app.models import CommonResponse, UserDataResponse, UserSchema
from app.services import AuthService

auth_router = APIRouter(prefix="/auth", tags=["Authorization"])


@auth_router.post(path="/register", response_model=CommonResponse)
async def register(
    user_data: UserSchema,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> CommonResponse:
    return await auth_service.register(user_data)


@auth_router.post(path="/login", response_model=UserDataResponse)
async def login(
    user_data: UserSchema,
    response: Response,
    service: Annotated[AuthService, Depends(get_auth_service)],
)-> UserDataResponse:
    return await service.login(data=user_data, response=response)


@auth_router.post(path="/logout", response_model=CommonResponse)
async def logout(response: Response)-> CommonResponse:
    return await AuthService.logout(response=response)


@auth_router.post(path="/refresh", response_model=CommonResponse)
async def refresh(
    request: Request,
    response: Response,
    service: Annotated[AuthService, Depends(get_auth_service)],
)-> CommonResponse:
    return await service.refresh(
        request=request,
        response=response,
    )
