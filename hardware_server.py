#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智核万炼® NexaForge AI - 硬件监控API服务器 v2.1
NexaForge AI Hardware Monitoring API Server
"""

import asyncio
import os
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from hardware import detector
from hardware.routes import router as api_router
from hardware.compute_routes import router as compute_router
from hardware.middleware import RateLimitMiddleware
from hardware.config import settings
from hardware.monitoring import create_instrumentator

app = FastAPI(
    title="智核万炼 - NexaForge AI 硬件监控API",
    description="企业级硬件检测与AI训练环境评估平台",
    version="2.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if settings.ENABLE_RATE_LIMIT:
    app.add_middleware(RateLimitMiddleware)

app.include_router(api_router, prefix=settings.API_PREFIX)
app.include_router(compute_router, prefix=settings.API_PREFIX)

instrumentator = create_instrumentator()
instrumentator.instrument(app).expose(app, endpoint="/metrics")


class ConnectionManager:
    """WebSocket 连接管理器"""

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections[:]:
            try:
                await connection.send_json(message)
            except Exception:
                self.disconnect(connection)


manager = ConnectionManager()


@app.get("/api/snapshot")
async def get_snapshot_legacy():
    """获取硬件快照 (兼容旧版本)"""
    try:
        snapshot = await asyncio.to_thread(detector.get_hardware_snapshot)
        detector.last_snapshot = snapshot
        recommendations = await asyncio.to_thread(detector.get_training_recommendations, snapshot)
        return {
            "snapshot": snapshot,
            "recommendations": recommendations
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={
                "error": "Failed to get hardware snapshot",
                "detail": str(e)
            }
        )


@app.get("/api/recommendations")
async def get_recommendations_legacy():
    """获取训练推荐 (兼容旧版本)"""
    snapshot = detector.get_hardware_snapshot()
    recommendations = detector.get_training_recommendations(snapshot)
    return recommendations


@app.get("/api/history")
async def get_history_legacy():
    """获取历史数据 (兼容旧版本)"""
    return detector.get_history()


@app.get("/api/stats/history")
async def get_stats_history():
    """获取统计历史数据 (趋势图用)"""
    history = detector.get_history()
    if not history:
        return []
    stats = []
    for h in history:
        try:
            snap = h.get("snapshot", h)
            cpu_data = snap.get("cpu", {})
            mem_data = snap.get("memory", {})
            gpu_data = snap.get("gpu", {})
            temp_data = snap.get("temperature", {})
            stats.append({
                "timestamp": snap.get("timestamp", ""),
                "cpu": cpu_data.get("percent", 0),
                "memory": mem_data.get("percent", 0),
                "gpu": gpu_data.get("devices", [{}])[0].get("utilization", 0) if gpu_data.get("devices") else 0,
                "score": snap.get("score", 0),
                "cpu_temp": temp_data.get("cpu_temp", 0),
                "gpu_temp": temp_data.get("gpu_temp", 0),
                "vram": gpu_data.get("devices", [{}])[0].get("memory_percent", 0) if gpu_data.get("devices") else 0,
            })
        except Exception:
            continue
    return stats


@app.get("/api/report/enterprise")
async def get_enterprise_report_legacy():
    """生成企业级评估报告 (兼容旧版本)"""
    report = await asyncio.to_thread(detector.generate_enterprise_report)
    return report


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket 实时监控"""
    await manager.connect(websocket)
    try:
        while True:
            snapshot = await asyncio.to_thread(detector.get_hardware_snapshot)
            recommendations = await asyncio.to_thread(detector.get_training_recommendations, snapshot)
            detector.last_snapshot = snapshot
            await manager.broadcast({
                "snapshot": snapshot,
                "recommendations": recommendations
            })
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "智核万炼 NexaForge AI",
        "version": "2.1.0",
        "description": "企业级硬件检测与AI训练环境评估平台",
        "docs": "/docs",
        "api": "/api/v1",
        "metrics": "/metrics"
    }


@app.get("/health")
async def health_check():
    """基础健康检查"""
    return {
        "status": "healthy",
        "service": "NexaForge AI Hardware Monitor",
        "version": "2.1.0"
    }


@app.get("/health/live")
async def liveness():
    """存活探针 - 检查服务是否存活"""
    return {
        "status": "alive",
        "timestamp": detector.get_hardware_snapshot()["timestamp"]
    }


@app.get("/health/ready")
async def readiness():
    """就绪探针 - 检查服务是否准备就绪"""
    try:
        cpu_info = detector.get_cpu_info()
        memory_info = detector.get_memory_info()

        is_ready = (
            cpu_info is not None and
            memory_info is not None and
            len(cpu_info) > 0 and
            len(memory_info) > 0
        )

        if is_ready:
            return {
                "status": "ready",
                "checks": {
                    "cpu": "ok",
                    "memory": "ok"
                }
            }
        else:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "not_ready",
                    "checks": {
                        "cpu": "ok" if cpu_info else "failed",
                        "memory": "ok" if memory_info else "failed"
                    }
                }
            )
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "error": str(e)
            }
        )


frontend_dist = Path(__file__).parent / settings.FRONTEND_DIST_DIR
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="react_app")
    print(f"✅ 前端应用已挂载: {frontend_dist}")
else:
    print(f"⚠️  未找到前端构建文件: {frontend_dist}")
    print("💡 请先运行: cd frontend && npm run build")


if __name__ == "__main__":
    print("=" * 60)
    print("智核万炼 NexaForge AI - 硬件监控服务 v2.1")
    print("=" * 60)
    print(f"\n🌐 访问地址: http://localhost:{settings.PORT}")
    print(f"📚 API文档:   http://localhost:{settings.PORT}/docs")
    print(f"🔌 WebSocket: ws://localhost:{settings.PORT}/ws")
    print(f"📊 监控指标:  http://localhost:{settings.PORT}/metrics")
    print(f"🔐 API版本:   {settings.API_PREFIX}")
    print(f"⚙️  认证:     {'启用' if settings.ENABLE_AUTH else '禁用'}")
    print(f"🚀 速率限制:  {'启用' if settings.ENABLE_RATE_LIMIT else '禁用'}")
    print(f"📈 监控:      {'启用' if True else '禁用'}")
    print("=" * 60 + "\n")

    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        log_level="info"
    )
