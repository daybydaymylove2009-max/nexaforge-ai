#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智核万炼® NexaForge AI - 后端主应用
Backend Main Application
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import uvicorn

from backend.api.routes import router

app = FastAPI(
    title="智核万炼® NexaForge AI",
    description="硬件实时监控与智能训练推荐系统 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载API路由
app.include_router(router)

# 挂载静态文件
frontend_dir = Path(__file__).parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

# 挂载 React 构建产物
react_dir = Path(__file__).parent.parent / "frontend" / "dist"
if react_dir.exists():
    app.mount("/", StaticFiles(directory=react_dir, html=True), name="react_app")


def main():
    try:
        print("="*60)
        print("智核万炼 NexaForge AI - 后端服务启动")
        print("="*60)
        print("\n服务启动中...")
        print("访问地址: http://localhost:8000")
        print("API文档: http://localhost:8000/docs")
        print("="*60 + "\n")
    except UnicodeEncodeError:
        print("NexaForge AI Backend Service Starting...")
    
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )


if __name__ == "__main__":
    main()
