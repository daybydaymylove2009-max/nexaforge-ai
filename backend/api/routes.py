#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智核万炼® NexaForge AI - API路由模块
API Routes Module
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
import asyncio

from backend.core.hardware_detector import detector

router = APIRouter()

# WebSocket连接管理器
class ConnectionManager:
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


@router.get("/api/snapshot", tags=["硬件监控"])
async def get_snapshot():
    """获取硬件快照"""
    snapshot = detector.get_hardware_snapshot()
    recommendations = detector.get_training_recommendations(snapshot)
    return JSONResponse(content={
        "snapshot": snapshot,
        "recommendations": recommendations
    })


@router.get("/api/recommendations", tags=["训练推荐"])
async def get_recommendations():
    """获取训练推荐配置"""
    snapshot = detector.get_hardware_snapshot()
    recommendations = detector.get_training_recommendations(snapshot)
    return JSONResponse(content=recommendations)


@router.get("/api/history", tags=["历史数据"])
async def get_history():
    """获取历史数据"""
    return JSONResponse(content=detector.get_history())


@router.get("/api/score", tags=["硬件评分"])
async def get_score():
    """获取硬件综合评分"""
    snapshot = detector.get_hardware_snapshot()
    score = detector.calculate_hardware_score(snapshot)
    return JSONResponse(content={"score": score})


@router.get("/api/system", tags=["系统信息"])
async def get_system_info():
    """获取系统信息"""
    return JSONResponse(content=detector.get_system_info())


@router.get("/api/cpu", tags=["CPU监控"])
async def get_cpu_info():
    """获取CPU信息"""
    return JSONResponse(content=detector.get_cpu_info())


@router.get("/api/memory", tags=["内存监控"])
async def get_memory_info():
    """获取内存信息"""
    return JSONResponse(content=detector.get_memory_info())


@router.get("/api/gpu", tags=["GPU监控"])
async def get_gpu_info():
    """获取GPU信息"""
    return JSONResponse(content=detector.get_gpu_info())


@router.get("/api/disk", tags=["磁盘监控"])
async def get_disk_info():
    """获取磁盘信息"""
    return JSONResponse(content=detector.get_disk_info())


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket实时监控"""
    await manager.connect(websocket)
    try:
        while True:
            snapshot = detector.get_hardware_snapshot()
            recommendations = detector.get_training_recommendations(snapshot)
            await manager.broadcast({
                "snapshot": snapshot,
                "recommendations": recommendations
            })
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)
