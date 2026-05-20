#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智核万炼® NexaForge AI - 认证模块
NexaForge AI Authentication
"""

from typing import Optional
from fastapi import Header, HTTPException


async def verify_api_key(x_api_key: Optional[str] = Header(None)) -> str:
    """
    验证 API Key
    
    如果启用了认证，则需要提供有效的 API Key
    """
    from .config import settings
    
    if settings.ENABLE_AUTH and settings.API_KEY:
        if not x_api_key or x_api_key != settings.API_KEY:
            raise HTTPException(
                status_code=403,
                detail="无效的 API Key"
            )
    
    return x_api_key or "anonymous"
