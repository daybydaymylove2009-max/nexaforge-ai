#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智核万炼® NexaForge AI - 配置管理模块
NexaForge AI Configuration Management
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False

    # 数据库配置
    DB_FILE: str = "nexaforge_v2.db"
    MAX_HISTORY: int = 1000

    # API 配置
    API_VERSION: str = "v1"
    API_PREFIX: str = "/api/v1"

    # 认证配置
    API_KEY: Optional[str] = None
    ENABLE_AUTH: bool = False

    # 速率限制
    ENABLE_RATE_LIMIT: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # 秒

    # 缓存配置
    ENABLE_CACHE: bool = True
    CACHE_TTL: int = 5  # 秒

    # 基准测试配置
    BENCHMARK_CPU_DURATION: float = 5.0
    BENCHMARK_STORAGE_SIZE: int = 100  # MB

    # 前端配置
    FRONTEND_DIST_DIR: str = "frontend/dist"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# 全局配置实例
settings = Settings()
