#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智核万炼® NexaForge AI - 硬件监控API服务器
Hardware Monitoring API Server
"""

import os
import sys
import json
import asyncio
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import uvicorn

from hardware_monitor import detector

# 创建FastAPI应用
app = FastAPI(
    title="智核万炼 - 硬件监控API",
    description="实时硬件监控与训练推荐系统",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 连接管理
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


@app.get("/api/snapshot")
async def get_snapshot():
    """获取硬件快照"""
    snapshot = await asyncio.to_thread(detector.get_hardware_snapshot)
    recommendations = await asyncio.to_thread(detector.get_training_recommendations, snapshot)
    return JSONResponse(content={
        "snapshot": snapshot,
        "recommendations": recommendations
    })


@app.get("/api/recommendations")
async def get_recommendations():
    """获取训练推荐"""
    snapshot = detector.get_hardware_snapshot()
    recommendations = detector.get_training_recommendations(snapshot)
    return JSONResponse(content=recommendations)


@app.get("/api/history")
async def get_history():
    """获取历史数据"""
    return JSONResponse(content=detector.get_history())


# 企业级高级检测API
@app.post("/api/advanced/health-check")
async def health_check():
    """硬件健康检查"""
    result = detector.check_hardware_health()
    return JSONResponse(content=result)


@app.post("/api/advanced/benchmark/cpu")
async def benchmark_cpu(duration: float = 5.0):
    """CPU性能基准测试"""
    result = detector.run_benchmark_cpu(duration=duration)
    return JSONResponse(content=result)


@app.post("/api/advanced/benchmark/gpu")
async def benchmark_gpu():
    """GPU性能基准测试"""
    result = detector.run_benchmark_gpu()
    return JSONResponse(content=result)


@app.post("/api/advanced/benchmark/memory")
async def benchmark_memory():
    """内存性能基准测试"""
    result = detector.run_benchmark_memory()
    return JSONResponse(content=result)


@app.post("/api/advanced/benchmark/storage")
async def benchmark_storage():
    """存储性能基准测试"""
    result = detector.run_benchmark_storage()
    return JSONResponse(content=result)


@app.post("/api/advanced/report")
async def generate_report():
    """生成企业级评估报告"""
    result = detector.generate_enterprise_report()
    return JSONResponse(content=result)

@app.get("/api/report/enterprise")
async def generate_ai_diagnostic_report(api_key: str = None):
    """生成专业的企业级AI大模型训练诊断报告 (受保护)"""
    # 工业级简单鉴权 (生产环境应使用环境变量)
    EXPECTED_KEY = "NEXA-PRO-2026"
    if api_key != EXPECTED_KEY:
        return JSONResponse(
            status_code=403,
            content={"error": "Unauthorized: 工业授权令牌无效或缺失。"}
        )
    result = detector.generate_ai_training_diagnostic_report()
    return JSONResponse(content=result)

@app.get("/api/stats/history")
async def get_stats_history(limit: int = 60):
    """获取历史统计数据用于趋势分析"""
    try:
        # 内部重用 detector 的加载逻辑
        history = detector._load_history()
        # 格式化为前端图表易读的结构
        chart_data = []
        for item in history:
            chart_data.append({
                "time": item["timestamp"][11:19], # 提取 HH:mm:ss
                "score": item.get("compute_ladder", [{}])[0].get("score", 0) if item.get("compute_ladder") else 0,
                "cpu": item.get("cpu", {}).get("percent", 0),
                "vram": item.get("gpu", {}).get("devices", [{}])[0].get("utilization", 0) if item.get("gpu", {}).get("devices") else 0
            })
        return JSONResponse(content=chart_data)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/api/advanced/benchmark/network")
async def benchmark_network():
    """网络性能基准测试"""
    result = detector.run_network_benchmark()
    return JSONResponse(content=result)

@app.post("/api/advanced/cpu/instructions")
async def check_cpu_instructions():
    """检查 CPU 指令集支持"""
    result = detector.check_cpu_instruction_sets()
    return JSONResponse(content=result)

@app.post("/api/advanced/system/processes")
async def analyze_processes():
    """分析系统进程资源占用"""
    result = detector.analyze_system_processes()
    return JSONResponse(content=result)

@app.post("/api/advanced/memory/virtual")
async def check_virtual_memory():
    """检查虚拟内存和 Swap 配置"""
    result = detector.check_virtual_memory()
    return JSONResponse(content=result)

@app.post("/api/advanced/system/logs")
async def check_logs():
    """检查系统日志中的硬件相关错误"""
    result = detector.check_system_logs()
    return JSONResponse(content=result)

@app.post("/api/advanced/detect")
async def advanced_detect(
    benchmark_cpu: bool = False,
    benchmark_gpu: bool = False,
    benchmark_memory: bool = False,
    benchmark_storage: bool = False,
    health_check: bool = True,
    generate_report: bool = True
):
    """运行高级检测（可配置）"""
    options = {
        "benchmark_cpu": benchmark_cpu,
        "benchmark_gpu": benchmark_gpu,
        "benchmark_memory": benchmark_memory,
        "benchmark_storage": benchmark_storage,
        "health_check": health_check,
        "generate_report": generate_report
    }
    result = detector.run_advanced_detection(options)
    return JSONResponse(content=result)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket实时监控"""
    await manager.connect(websocket)
    try:
        while True:
            snapshot = await asyncio.to_thread(detector.get_hardware_snapshot)
            recommendations = await asyncio.to_thread(detector.get_training_recommendations, snapshot)
            await manager.broadcast({
                "snapshot": snapshot,
                "recommendations": recommendations
            })
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)


# 挂载React构建文件 - 必须在API路由之后！
react_dist_dir = Path(__file__).parent / "frontend" / "dist"
if react_dist_dir.exists():
    app.mount("/", StaticFiles(directory=react_dist_dir, html=True), name="react_app")
    print(f"[OK] React应用已挂载: {react_dist_dir}")
else:
    print("[WARN] 未找到React构建文件，请先运行 npm run build")


if __name__ == "__main__":
    print("="*60)
    print("NexaForge AI - 硬件监控服务")
    print("="*60)
    print(f"\n[INFO] 服务启动中...")
    print(f"[URL] 访问地址: http://localhost:8000")
    print(f"[DOCS] API文档: http://localhost:8000/docs")
    print("="*60 + "\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
