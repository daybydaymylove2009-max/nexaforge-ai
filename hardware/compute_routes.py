#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智核万炼 NexaForge AI - 算力评估API路由
NexaForge AI Compute Evaluation API Routes
"""

import asyncio
from typing import Optional
from fastapi import APIRouter, Depends, Query, BackgroundTasks
from pydantic import BaseModel

from .detector import detector
from .models import APIResponse
from .config import settings
from .auth import verify_api_key


router = APIRouter(prefix="/compute", tags=["算力评估"])


class GPUEvaluateRequest(BaseModel):
    """GPU评估请求"""
    run_benchmark: bool = False
    benchmark_duration: int = 5


class ModelAddRequest(BaseModel):
    """添加自定义模型请求"""
    name: str
    params: int
    context_length: int = 4096
    vocab_size: int = 32000
    recommended_vram_gb: Optional[float] = None
    finetune_vram_gb: Optional[float] = None
    lora_vram_gb: Optional[float] = None
    qlora_vram_gb: Optional[float] = None
    architecture: str = "自定义"
    provider: str = "自定义"


@router.get("/evaluation/comprehensive", response_model=APIResponse)
async def get_comprehensive_evaluation(api_key: str = Depends(verify_api_key)):
    """获取综合算力评估报告"""
    try:
        from .compute_evaluator import ComputeEvaluator

        snapshot = await asyncio.to_thread(detector.get_hardware_snapshot)
        evaluator = ComputeEvaluator(snapshot)
        report = evaluator.generate_comprehensive_report()

        return APIResponse(code=200, message="success", data=report)
    except Exception as e:
        return APIResponse(code=500, message=f"综合评估失败: {str(e)}", data=None)


@router.get("/gpu/benchmark", response_model=APIResponse)
async def run_gpu_benchmark(
    duration: int = Query(5, ge=3, le=30),
    api_key: str = Depends(verify_api_key)
):
    """运行GPU真实算力基准测试"""
    try:
        from .compute_evaluator import ComputeEvaluator

        snapshot = await asyncio.to_thread(detector.get_hardware_snapshot)
        evaluator = ComputeEvaluator(snapshot)
        result = await asyncio.to_thread(evaluator.benchmark_gpu_real, duration)

        return APIResponse(code=200, message="GPU基准测试完成", data=result)
    except Exception as e:
        return APIResponse(code=500, message=f"基准测试失败: {str(e)}", data=None)


@router.get("/gpu/info", response_model=APIResponse)
async def get_gpu_detailed_info(api_key: str = Depends(verify_api_key)):
    """获取GPU详细信息"""
    try:
        from .compute_evaluator import ComputeEvaluator

        snapshot = await asyncio.to_thread(detector.get_hardware_snapshot)
        evaluator = ComputeEvaluator(snapshot)

        gpu_name = evaluator.detect_gpu_model()
        vram_gb = evaluator.get_vram_gb()
        tflops, gpu_info = evaluator.estimate_gpu_tflops()
        rankings = evaluator.get_gpu_ranking()

        return APIResponse(code=200, message="success", data={
            "gpu_name": gpu_name,
            "vram_gb": round(vram_gb, 1),
            "tflops_fp16": round(tflops, 1),
            "gpu_info": gpu_info,
            "rankings": rankings[:20],
        })
    except Exception as e:
        return APIResponse(code=500, message=f"获取GPU信息失败: {str(e)}", data=None)


@router.get("/pretraining", response_model=APIResponse)
async def evaluate_pretraining(
    dataset_tokens: int = Query(100_000_000_000, ge=1_000_000_000),
    api_key: str = Depends(verify_api_key)
):
    """评估预训练能力"""
    try:
        from .compute_evaluator import ComputeEvaluator

        snapshot = await asyncio.to_thread(detector.get_hardware_snapshot)
        evaluator = ComputeEvaluator(snapshot)
        result = evaluator.evaluate_pretraining_capability(dataset_tokens)

        return APIResponse(code=200, message="success", data=result)
    except Exception as e:
        return APIResponse(code=500, message=f"预训练评估失败: {str(e)}", data=None)


@router.get("/finetuning", response_model=APIResponse)
async def evaluate_finetuning(api_key: str = Depends(verify_api_key)):
    """评估微调能力"""
    try:
        from .compute_evaluator import ComputeEvaluator

        snapshot = await asyncio.to_thread(detector.get_hardware_snapshot)
        evaluator = ComputeEvaluator(snapshot)
        result = evaluator.evaluate_finetuning_capability()

        return APIResponse(code=200, message="success", data=result)
    except Exception as e:
        return APIResponse(code=500, message=f"微调评估失败: {str(e)}", data=None)


@router.get("/self-improvement", response_model=APIResponse)
async def evaluate_self_improvement(api_key: str = Depends(verify_api_key)):
    """评估自进化能力"""
    try:
        from .compute_evaluator import ComputeEvaluator

        snapshot = await asyncio.to_thread(detector.get_hardware_snapshot)
        evaluator = ComputeEvaluator(snapshot)
        result = evaluator.evaluate_self_improvement_capability()

        return APIResponse(code=200, message="success", data=result)
    except Exception as e:
        return APIResponse(code=500, message=f"自进化评估失败: {str(e)}", data=None)


@router.get("/models", response_model=APIResponse)
async def get_model_database(api_key: str = Depends(verify_api_key)):
    """获取支持的模型数据库"""
    try:
        from .compute_evaluator import ModelDatabase

        models = ModelDatabase.get_all_models()
        model_list = [{
            "name": m.name,
            "params_b": m.params / 1e9,
            "context_length": m.context_length,
            "recommended_vram_gb": round(m.recommended_vram_gb, 1),
            "finetune_vram_gb": round(m.finetune_vram_gb, 1),
            "lora_vram_gb": round(m.lora_vram_gb, 1),
            "qlora_vram_gb": round(m.qlora_vram_gb, 1),
            "architecture": m.architecture,
            "provider": m.provider,
        } for m in models]

        return APIResponse(code=200, message="success", data={
            "total_models": len(model_list),
            "models": model_list,
        })
    except Exception as e:
        return APIResponse(code=500, message=f"获取模型数据库失败: {str(e)}", data=None)


@router.post("/models/custom", response_model=APIResponse)
async def add_custom_model(request: ModelAddRequest, api_key: str = Depends(verify_api_key)):
    """添加自定义模型到数据库"""
    try:
        from .compute_evaluator import ModelDatabase

        model = ModelDatabase.add_custom_model(
            name=request.name, params=request.params,
            context_length=request.context_length, vocab_size=request.vocab_size,
            recommended_vram_gb=request.recommended_vram_gb,
            finetune_vram_gb=request.finetune_vram_gb,
            lora_vram_gb=request.lora_vram_gb,
            qlora_vram_gb=request.qlora_vram_gb,
            architecture=request.architecture, provider=request.provider,
        )

        return APIResponse(code=200, message=f"自定义模型 '{request.name}' 添加成功", data={
            "name": model.name, "params_b": model.params / 1e9,
            "recommended_vram_gb": round(model.recommended_vram_gb, 1),
        })
    except Exception as e:
        return APIResponse(code=500, message=f"添加自定义模型失败: {str(e)}", data=None)


@router.get("/gpus", response_model=APIResponse)
async def get_gpu_database(api_key: str = Depends(verify_api_key)):
    """获取GPU数据库"""
    try:
        from .compute_evaluator import GPUDatabase

        gpus = GPUDatabase.get_all_gpus()
        gpu_list = [{
            "name": g.name, "tflops_fp16_tensor": g.tflops_fp16_tensor,
            "vram_gb": g.vram_gb, "bandwidth_gb_s": g.bandwidth_gb_s,
            "tdp_w": g.tdp_w, "architecture": g.architecture,
        } for g in gpus]

        return APIResponse(code=200, message="success", data={
            "total_gpus": len(gpu_list), "gpus": gpu_list,
        })
    except Exception as e:
        return APIResponse(code=500, message=f"获取GPU数据库失败: {str(e)}", data=None)


@router.get("/score", response_model=APIResponse)
async def get_overall_score(api_key: str = Depends(verify_api_key)):
    """获取综合评分"""
    try:
        from .compute_evaluator import ComputeEvaluator

        snapshot = await asyncio.to_thread(detector.get_hardware_snapshot)
        evaluator = ComputeEvaluator(snapshot)
        tflops, _ = evaluator.estimate_gpu_tflops()
        vram_gb = evaluator.get_vram_gb()
        score = evaluator._calculate_overall_score(tflops, vram_gb)

        return APIResponse(code=200, message="success", data={
            "gpu_name": evaluator.detect_gpu_model(),
            "tflops_fp16": round(tflops, 1),
            "vram_gb": round(vram_gb, 1),
            "score": score,
        })
    except Exception as e:
        return APIResponse(code=500, message=f"获取评分失败: {str(e)}", data=None)
