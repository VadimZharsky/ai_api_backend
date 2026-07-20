from typing import Literal

from fastapi import Request, Response


class CookieHandler:
    _HTTPONLY: bool = True
    _ACCESS_KEY: str = "access_token"
    _REFRESH_KEY: str = "refresh_token"
    _SAME_SITE: Literal["lax", "strict", "none"] = "lax"
    _REFRESH_PATH: str = "/auth/refresh"

    @staticmethod
    def get_refresh_token(request: Request) -> str | None:
        return request.cookies.get(CookieHandler._REFRESH_KEY)

    @staticmethod
    def get_access_token(request: Request) -> str | None:
        return request.cookies.get(CookieHandler._ACCESS_KEY)
    
    @staticmethod
    def set_access_token(response: Response, token: str | None) -> None:
        if token is None:
            return
        response.set_cookie(
            key=CookieHandler._ACCESS_KEY,
            value=token,
            httponly=CookieHandler._HTTPONLY,
            samesite=CookieHandler._SAME_SITE,
        )
        
    @staticmethod
    def set_refresh_token(response: Response, token: str | None) -> None:
        if token is None:
            return
        response.set_cookie(
            key=CookieHandler._REFRESH_KEY,
            value=token,
            httponly=CookieHandler._HTTPONLY,
            samesite=CookieHandler._SAME_SITE,
            path=CookieHandler._REFRESH_PATH,
        )

    @staticmethod
    def remove(response: Response) -> None:
        response.delete_cookie(
            key=CookieHandler._ACCESS_KEY,
            httponly=CookieHandler._HTTPONLY,
            samesite=CookieHandler._SAME_SITE,
        )
        response.delete_cookie(
            key=CookieHandler._REFRESH_KEY,
            httponly=CookieHandler._HTTPONLY,
            samesite=CookieHandler._SAME_SITE,
            path=CookieHandler._REFRESH_PATH,
        )
