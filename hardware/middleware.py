#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智核万炼® NexaForge AI - 认证和中间件模块
NexaForge AI Authentication and Middleware
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable

from .config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    """速率限制中间件"""

    def __init__(self, app):
        super().__init__(app)
        self.requests = {}
        self.window = settings.RATE_LIMIT_WINDOW
        self.max_requests = settings.RATE_LIMIT_REQUESTS

    async def dispatch(self, request: Request, call_next: Callable):
        if not settings.ENABLE_RATE_LIMIT:
            return await call_next(request)

        client_ip = request.client.host
        current_time = int(__import__('time').time())

        if client_ip not in self.requests:
            self.requests[client_ip] = []

        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if current_time - req_time < self.window
        ]

        if len(self.requests[client_ip]) >= self.max_requests:
            return JSONResponse(
                status_code=429,
                content={
                    "code": 429,
                    "message": "请求过于频繁，请稍后再试",
                    "timestamp": __import__('datetime').datetime.now().isoformat()
                }
            )

        self.requests[client_ip].append(current_time)
        return await call_next(request)


async def verify_api_key_or_none(x_api_key: str = None) -> str:
    """验证 API Key (可选)"""
    if settings.ENABLE_AUTH and settings.API_KEY:
        if not x_api_key or x_api_key != settings.API_KEY:
            raise HTTPException(
                status_code=403,
                detail="无效的 API Key"
            )
    return x_api_key or "anonymous"


def create_auth_dependency():
    """创建认证依赖"""

    async def dependency(x_api_key: str = None) -> str:
        return await verify_api_key_or_none(x_api_key)

    return dependency
