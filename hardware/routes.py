#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智核万炼® NexaForge AI - API 路由模块
NexaForge AI API Routes
"""

import asyncio
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Header, Query, BackgroundTasks
from fastapi.responses import JSONResponse

from .detector import detector
from .models import (
    APIResponse,
    HardwareSnapshot,
    TaskStatus,
    BenchmarkResult,
    HealthCheckResult,
    TrainingRecommendation,
    EnterpriseReport
)
from .config import settings

router = APIRouter()

task_manager = {}


def verify_api_key(x_api_key: Optional[str] = Header(None)) -> str:
    """验证 API Key"""
    if settings.ENABLE_AUTH and settings.API_KEY:
        if not x_api_key or x_api_key != settings.API_KEY:
            raise HTTPException(
                status_code=403,
                detail="无效的 API Key"
            )
    return x_api_key or "anonymous"


@router.get("/snapshot", response_model=APIResponse)
async def get_snapshot(api_key: str = Depends(verify_api_key)):
    """获取完整硬件快照"""
    try:
        snapshot = await asyncio.to_thread(detector.get_hardware_snapshot)
        recommendations = await asyncio.to_thread(detector.get_training_recommendations, snapshot)
        return APIResponse(
            code=200,
            message="success",
            data={
                "snapshot": snapshot,
                "recommendations": recommendations
            }
        )
    except Exception as e:
        return APIResponse(
            code=500,
            message=f"获取快照失败: {str(e)}",
            data=None
        )


@router.get("/cpu", response_model=APIResponse)
async def get_cpu_info(api_key: str = Depends(verify_api_key)):
    """获取 CPU 信息"""
    try:
        cpu_info = await asyncio.to_thread(detector.get_cpu_info)
        return APIResponse(
            code=200,
            message="success",
            data=cpu_info
        )
    except Exception as e:
        return APIResponse(
            code=500,
            message=f"获取 CPU 信息失败: {str(e)}",
            data=None
        )


@router.get("/memory", response_model=APIResponse)
async def get_memory_info(api_key: str = Depends(verify_api_key)):
    """获取内存信息"""
    try:
        memory_info = await asyncio.to_thread(detector.get_memory_info)
        return APIResponse(
            code=200,
            message="success",
            data=memory_info
        )
    except Exception as e:
        return APIResponse(
            code=500,
            message=f"获取内存信息失败: {str(e)}",
            data=None
        )


@router.get("/gpu", response_model=APIResponse)
async def get_gpu_info(api_key: str = Depends(verify_api_key)):
    """获取 GPU 信息"""
    try:
        gpu_info = await asyncio.to_thread(detector.get_gpu_info)
        return APIResponse(
            code=200,
            message="success",
            data=gpu_info
        )
    except Exception as e:
        return APIResponse(
            code=500,
            message=f"获取 GPU 信息失败: {str(e)}",
            data=None
        )


@router.get("/cuda", response_model=APIResponse)
async def get_cuda_info(api_key: str = Depends(verify_api_key)):
    """获取 CUDA 信息"""
    try:
        cuda_info = await asyncio.to_thread(detector.get_cuda_info)
        return APIResponse(
            code=200,
            message="success",
            data=cuda_info
        )
    except Exception as e:
        return APIResponse(
            code=500,
            message=f"获取 CUDA 信息失败: {str(e)}",
            data=None
        )


@router.get("/history", response_model=APIResponse)
async def get_history(
    limit: int = Query(60, ge=1, le=1000, description="返回记录数量"),
    api_key: str = Depends(verify_api_key)
):
    """获取历史数据"""
    try:
        history = detector.get_history()
        limited_history = history[-limit:] if len(history) > limit else history
        return APIResponse(
            code=200,
            message="success",
            data={
                "total": len(history),
                "returned": len(limited_history),
                "history": limited_history
            }
        )
    except Exception as e:
        return APIResponse(
            code=500,
            message=f"获取历史数据失败: {str(e)}",
            data=None
        )


@router.post("/benchmark/cpu", response_model=APIResponse)
async def benchmark_cpu(
    duration: float = Query(5.0, ge=1.0, le=60.0, description="测试持续时间(秒)"),
    background_tasks: BackgroundTasks = BackgroundTasks,
    api_key: str = Depends(verify_api_key)
):
    """CPU 性能基准测试"""
    try:
        result = await asyncio.to_thread(detector.run_benchmark_cpu, duration)
        return APIResponse(
            code=200,
            message="CPU 基准测试完成",
            data=result
        )
    except Exception as e:
        return APIResponse(
            code=500,
            message=f"CPU 基准测试失败: {str(e)}",
            data=None
        )


@router.post("/benchmark/memory", response_model=APIResponse)
async def benchmark_memory(api_key: str = Depends(verify_api_key)):
    """内存性能基准测试"""
    try:
        result = await asyncio.to_thread(detector.run_benchmark_memory)
        return APIResponse(
            code=200,
            message="内存基准测试完成",
            data=result
        )
    except Exception as e:
        return APIResponse(
            code=500,
            message=f"内存基准测试失败: {str(e)}",
            data=None
        )


@router.post("/health-check", response_model=APIResponse)
async def health_check(api_key: str = Depends(verify_api_key)):
    """硬件健康检查"""
    try:
        result = await asyncio.to_thread(detector.check_hardware_health)
        return APIResponse(
            code=200,
            message="健康检查完成",
            data=result
        )
    except Exception as e:
        return APIResponse(
            code=500,
            message=f"健康检查失败: {str(e)}",
            data=None
        )


@router.get("/report/enterprise", response_model=APIResponse)
async def get_enterprise_report(api_key: str = Depends(verify_api_key)):
    """生成企业级评估报告"""
    try:
        result = await asyncio.to_thread(detector.generate_enterprise_report)
        return APIResponse(
            code=200,
            message="报告生成成功",
            data=result
        )
    except Exception as e:
        return APIResponse(
            code=500,
            message=f"报告生成失败: {str(e)}",
            data=None
        )


@router.get("/recommendations", response_model=APIResponse)
async def get_recommendations(api_key: str = Depends(verify_api_key)):
    """获取训练推荐"""
    try:
        snapshot = await asyncio.to_thread(detector.get_hardware_snapshot)
        recommendations = await asyncio.to_thread(detector.get_training_recommendations, snapshot)
        return APIResponse(
            code=200,
            message="success",
            data=recommendations
        )
    except Exception as e:
        return APIResponse(
            code=500,
            message=f"获取推荐失败: {str(e)}",
            data=None
        )


@router.get("/system", response_model=APIResponse)
async def get_system_info(api_key: str = Depends(verify_api_key)):
    """获取系统信息"""
    try:
        info = await asyncio.to_thread(detector.get_system_info)
        return APIResponse(
            code=200,
            message="success",
            data=info
        )
    except Exception as e:
        return APIResponse(
            code=500,
            message=f"获取系统信息失败: {str(e)}",
            data=None
        )


@router.get("/disk", response_model=APIResponse)
async def get_disk_info(api_key: str = Depends(verify_api_key)):
    """获取磁盘信息"""
    try:
        info = await asyncio.to_thread(detector.get_disk_info)
        return APIResponse(
            code=200,
            message="success",
            data=info
        )
    except Exception as e:
        return APIResponse(
            code=500,
            message=f"获取磁盘信息失败: {str(e)}",
            data=None
        )


@router.get("/network", response_model=APIResponse)
async def get_network_info(api_key: str = Depends(verify_api_key)):
    """获取网络信息"""
    try:
        info = await asyncio.to_thread(detector.get_network_info)
        return APIResponse(
            code=200,
            message="success",
            data=info
        )
    except Exception as e:
        return APIResponse(
            code=500,
            message=f"获取网络信息失败: {str(e)}",
            data=None
        )


@router.get("/power", response_model=APIResponse)
async def get_power_info(api_key: str = Depends(verify_api_key)):
    """获取电源信息"""
    try:
        info = await asyncio.to_thread(detector.get_power_info)
        return APIResponse(
            code=200,
            message="success",
            data=info
        )
    except Exception as e:
        return APIResponse(
            code=500,
            message=f"获取电源信息失败: {str(e)}",
            data=None
        )


@router.get("/ai-frameworks", response_model=APIResponse)
async def get_ai_frameworks(api_key: str = Depends(verify_api_key)):
    """获取 AI 框架信息"""
    try:
        info = await asyncio.to_thread(detector.get_ai_framework_info)
        return APIResponse(
            code=200,
            message="success",
            data=info
        )
    except Exception as e:
        return APIResponse(
            code=500,
            message=f"获取 AI 框架信息失败: {str(e)}",
            data=None
        )
