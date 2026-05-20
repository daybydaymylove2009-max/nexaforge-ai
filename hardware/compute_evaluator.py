#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智核万炼® NexaForge AI - 综合算力评估器
NexaForge AI Comprehensive Compute Evaluator
"""

import time
import math
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

try:
    import torch
    TORCH_AVAILABLE = torch.cuda.is_available()
except Exception:
    TORCH_AVAILABLE = False


@dataclass
class GPUInfo:
    """GPU信息"""
    name: str
    tflops_fp32: float
    tflops_fp16: float
    tflops_fp16_tensor: float
    vram_gb: float
    bandwidth_gb_s: float
    tdp_w: int
    architecture: str
    compute_capability: str


@dataclass
class ModelInfo:
    """模型信息"""
    name: str
    params: int
    context_length: int
    vocab_size: int
    recommended_vram_gb: float
    training_tflops_days: float
    finetune_vram_gb: float
    lora_vram_gb: float
    qlora_vram_gb: float
    architecture: str
    provider: str


class GPUDatabase:
    """GPU数据库"""

    # 主流GPU理论算力数据库
    GPUs = {
        # NVIDIA RTX 40 系列
        "RTX 4090": GPUInfo(
            name="NVIDIA GeForce RTX 4090",
            tflops_fp32=82.58,
            tflops_fp16=82.58,
            tflops_fp16_tensor=165.2,
            vram_gb=24,
            bandwidth_gb_s=1008,
            tdp_w=450,
            architecture="Ada Lovelace",
            compute_capability="8.9"
        ),
        "RTX 4080 Super": GPUInfo(
            name="NVIDIA GeForce RTX 4080 Super",
            tflops_fp32=52.2,
            tflops_fp16=52.2,
            tflops_fp16_tensor=104.8,
            vram_gb=16,
            bandwidth_gb_s=736,
            tdp_w=320,
            architecture="Ada Lovelace",
            compute_capability="8.9"
        ),
        "RTX 4080": GPUInfo(
            name="NVIDIA GeForce RTX 4080",
            tflops_fp32=48.7,
            tflops_fp16=48.7,
            tflops_fp16_tensor=117.5,
            vram_gb=16,
            bandwidth_gb_s=716.8,
            tdp_w=320,
            architecture="Ada Lovelace",
            compute_capability="8.9"
        ),
        "RTX 4070 Ti Super": GPUInfo(
            name="NVIDIA GeForce RTX 4070 Ti Super",
            tflops_fp32=44.1,
            tflops_fp16=44.1,
            tflops_fp16_tensor=88.2,
            vram_gb=16,
            bandwidth_gb_s=672,
            tdp_w=285,
            architecture="Ada Lovelace",
            compute_capability="8.9"
        ),
        "RTX 4070 Ti": GPUInfo(
            name="NVIDIA GeForce RTX 4070 Ti",
            tflops_fp32=40.09,
            tflops_fp16=40.09,
            tflops_fp16_tensor=80.2,
            vram_gb=12,
            bandwidth_gb_s=672,
            tdp_w=285,
            architecture="Ada Lovelace",
            compute_capability="8.9"
        ),
        "RTX 4070 Super": GPUInfo(
            name="NVIDIA GeForce RTX 4070 Super",
            tflops_fp32=35.5,
            tflops_fp16=35.5,
            tflops_fp16_tensor=71.0,
            vram_gb=12,
            bandwidth_gb_s=504,
            tdp_w=220,
            architecture="Ada Lovelace",
            compute_capability="8.9"
        ),
        "RTX 4070": GPUInfo(
            name="NVIDIA GeForce RTX 4070",
            tflops_fp32=29.1,
            tflops_fp16=29.1,
            tflops_fp16_tensor=65.5,
            vram_gb=12,
            bandwidth_gb_s=504,
            tdp_w=200,
            architecture="Ada Lovelace",
            compute_capability="8.9"
        ),
        "RTX 4060 Ti": GPUInfo(
            name="NVIDIA GeForce RTX 4060 Ti",
            tflops_fp32=22.1,
            tflops_fp16=22.1,
            tflops_fp16_tensor=44.2,
            vram_gb=16,
            bandwidth_gb_s=288,
            tdp_w=165,
            architecture="Ada Lovelace",
            compute_capability="8.9"
        ),
        "RTX 4060": GPUInfo(
            name="NVIDIA GeForce RTX 4060",
            tflops_fp32=15.1,
            tflops_fp16=15.1,
            tflops_fp16_tensor=30.2,
            vram_gb=8,
            bandwidth_gb_s=272,
            tdp_w=115,
            architecture="Ada Lovelace",
            compute_capability="8.9"
        ),

        # NVIDIA RTX 30 系列
        "RTX 3090 Ti": GPUInfo(
            name="NVIDIA GeForce RTX 3090 Ti",
            tflops_fp32=40.0,
            tflops_fp16=40.0,
            tflops_fp16_tensor=80.0,
            vram_gb=24,
            bandwidth_gb_s=1008,
            tdp_w=450,
            architecture="Ampere",
            compute_capability="8.6"
        ),
        "RTX 3090": GPUInfo(
            name="NVIDIA GeForce RTX 3090",
            tflops_fp32=35.58,
            tflops_fp16=35.58,
            tflops_fp16_tensor=71.0,
            vram_gb=24,
            bandwidth_gb_s=936,
            tdp_w=350,
            architecture="Ampere",
            compute_capability="8.6"
        ),
        "RTX 3080 Ti": GPUInfo(
            name="NVIDIA GeForce RTX 3080 Ti",
            tflops_fp32=34.1,
            tflops_fp16=34.1,
            tflops_fp16_tensor=61.9,
            vram_gb=12,
            bandwidth_gb_s=912,
            tdp_w=350,
            architecture="Ampere",
            compute_capability="8.6"
        ),
        "RTX 3080": GPUInfo(
            name="NVIDIA GeForce RTX 3080",
            tflops_fp32=29.77,
            tflops_fp16=29.77,
            tflops_fp16_tensor=59.4,
            vram_gb=10,
            bandwidth_gb_s=760,
            tdp_w=320,
            architecture="Ampere",
            compute_capability="8.6"
        ),
        "RTX 3070 Ti": GPUInfo(
            name="NVIDIA GeForce RTX 3070 Ti",
            tflops_fp32=21.7,
            tflops_fp16=21.7,
            tflops_fp16_tensor=43.4,
            vram_gb=8,
            bandwidth_gb_s=608,
            tdp_w=290,
            architecture="Ampere",
            compute_capability="8.6"
        ),
        "RTX 3070": GPUInfo(
            name="NVIDIA GeForce RTX 3070",
            tflops_fp32=19.5,
            tflops_fp16=19.5,
            tflops_fp16_tensor=39.5,
            vram_gb=8,
            bandwidth_gb_s=608,
            tdp_w=220,
            architecture="Ampere",
            compute_capability="8.6"
        ),
        "RTX 3060 Ti": GPUInfo(
            name="NVIDIA GeForce RTX 3060 Ti",
            tflops_fp32=12.7,
            tflops_fp16=12.7,
            tflops_fp16_tensor=25.4,
            vram_gb=8,
            bandwidth_gb_s=448,
            tdp_w=200,
            architecture="Ampere",
            compute_capability="8.6"
        ),
        "RTX 3060": GPUInfo(
            name="NVIDIA GeForce RTX 3060",
            tflops_fp32=12.7,
            tflops_fp16=12.7,
            tflops_fp16_tensor=25.5,
            vram_gb=12,
            bandwidth_gb_s=360,
            tdp_w=170,
            architecture="Ampere",
            compute_capability="8.6"
        ),

        # NVIDIA RTX 20 系列
        "RTX 2080 Ti": GPUInfo(
            name="NVIDIA GeForce RTX 2080 Ti",
            tflops_fp32=13.45,
            tflops_fp16=13.45,
            tflops_fp16_tensor=26.9,
            vram_gb=11,
            bandwidth_gb_s=616,
            tdp_w=250,
            architecture="Turing",
            compute_capability="7.5"
        ),
        "RTX 2080 Super": GPUInfo(
            name="NVIDIA GeForce RTX 2080 Super",
            tflops_fp32=11.15,
            tflops_fp16=11.15,
            tflops_fp16_tensor=22.3,
            vram_gb=8,
            bandwidth_gb_s=496,
            tdp_w=215,
            architecture="Turing",
            compute_capability="7.5"
        ),
        "RTX 2080": GPUInfo(
            name="NVIDIA GeForce RTX 2080",
            tflops_fp32=10.07,
            tflops_fp16=10.07,
            tflops_fp16_tensor=20.1,
            vram_gb=8,
            bandwidth_gb_s=448,
            tdp_w=215,
            architecture="Turing",
            compute_capability="7.5"
        ),

        # NVIDIA数据中心 GPU
        "A100 80GB": GPUInfo(
            name="NVIDIA A100 80GB",
            tflops_fp32=19.5,
            tflops_fp16=19.5,
            tflops_fp16_tensor=312.0,
            vram_gb=80,
            bandwidth_gb_s=2039,
            tdp_w=400,
            architecture="Ampere",
            compute_capability="8.0"
        ),
        "A100 40GB": GPUInfo(
            name="NVIDIA A100 40GB",
            tflops_fp32=19.5,
            tflops_fp16=19.5,
            tflops_fp16_tensor=312.0,
            vram_gb=40,
            bandwidth_gb_s=1555,
            tdp_w=400,
            architecture="Ampere",
            compute_capability="8.0"
        ),
        "A800 80GB": GPUInfo(
            name="NVIDIA A800 80GB",
            tflops_fp32=19.5,
            tflops_fp16=19.5,
            tflops_fp16_tensor=312.0,
            vram_gb=80,
            bandwidth_gb_s=2039,
            tdp_w=400,
            architecture="Ampere",
            compute_capability="8.0"
        ),
        "H100 80GB": GPUInfo(
            name="NVIDIA H100 80GB",
            tflops_fp32=51.0,
            tflops_fp16=51.0,
            tflops_fp16_tensor=395.8,
            vram_gb=80,
            bandwidth_gb_s=3350,
            tdp_w=700,
            architecture="Hopper",
            compute_capability="9.0"
        ),
        "H100 SXM": GPUInfo(
            name="NVIDIA H100 SXM5",
            tflops_fp32=51.0,
            tflops_fp16=51.0,
            tflops_fp16_tensor=989.0,
            vram_gb=80,
            bandwidth_gb_s=3350,
            tdp_w=700,
            architecture="Hopper",
            compute_capability="9.0"
        ),
        "L40S": GPUInfo(
            name="NVIDIA L40S",
            tflops_fp32=65.0,
            tflops_fp16=65.0,
            tflops_fp16_tensor=130.0,
            vram_gb=48,
            bandwidth_gb_s=864,
            tdp_w=350,
            architecture="Ada Lovelace",
            compute_capability="8.9"
        ),

        # AMD GPU
        "RX 7900 XTX": GPUInfo(
            name="AMD Radeon RX 7900 XTX",
            tflops_fp32=61.0,
            tflops_fp16=122.0,
            tflops_fp16_tensor=0,  # AMD 不支持Tensor Core
            vram_gb=24,
            bandwidth_gb_s=960,
            tdp_w=355,
            architecture="RDNA 3",
            compute_capability="N/A"
        ),
        "RX 7900 XT": GPUInfo(
            name="AMD Radeon RX 7900 XT",
            tflops_fp32=51.0,
            tflops_fp16=102.0,
            tflops_fp16_tensor=0,
            vram_gb=20,
            bandwidth_gb_s=800,
            tdp_w=315,
            architecture="RDNA 3",
            compute_capability="N/A"
        ),

        # Apple Silicon
        "M3 Max": GPUInfo(
            name="Apple M3 Max",
            tflops_fp32=0,
            tflops_fp16=21.0,
            tflops_fp16_tensor=21.0,
            vram_gb=128,
            bandwidth_gb_s=800,
            tdp_w=92,
            architecture="Apple GPU",
            compute_capability="N/A"
        ),
        "M2 Ultra": GPUInfo(
            name="Apple M2 Ultra",
            tflops_fp32=0,
            tflops_fp16=27.0,
            tflops_fp16_tensor=27.0,
            vram_gb=192,
            bandwidth_gb_s=800,
            tdp_w=125,
            architecture="Apple GPU",
            compute_capability="N/A"
        ),
        "M2 Max": GPUInfo(
            name="Apple M2 Max",
            tflops_fp32=0,
            tflops_fp16=13.5,
            tflops_fp16_tensor=13.5,
            vram_gb=96,
            bandwidth_gb_s=400,
            tdp_w=86,
            architecture="Apple GPU",
            compute_capability="N/A"
        ),
    }

    @classmethod
    def match_gpu(cls, gpu_name: str) -> Optional[GPUInfo]:
        """根据GPU名称匹配数据库中的GPU"""
        if not gpu_name:
            return None

        gpu_name_lower = gpu_name.lower()

        # 精确匹配
        for key, gpu in cls.GPUs.items():
            if key.lower() in gpu_name_lower or gpu_name_lower in key.lower():
                return gpu

        # 部分匹配
        for key, gpu in cls.GPUs.items():
            key_parts = key.lower().split()
            gpu_name_parts = gpu_name_lower.split()

            # 检查主要部分
            for part in gpu_name_parts:
                if part in key_parts:
                    return gpu

        return None

    @classmethod
    def get_all_gpus(cls) -> List[GPUInfo]:
        """获取所有GPU列表"""
        return list(cls.GPUs.values())


class ModelDatabase:
    """模型数据库"""

    # 主流开源模型
    Models = {
        # Meta Llama 系列
        "Llama-2-70B": ModelInfo(
            name="Llama 2 70B",
            params=70_000_000_000,
            context_length=4096,
            vocab_size=32000,
            recommended_vram_gb=148,
            training_tflops_days=1400,
            finetune_vram_gb=140,
            lora_vram_gb=70,
            qlora_vram_gb=42,
            architecture="LLaMA",
            provider="Meta"
        ),
        "Llama-2-34B": ModelInfo(
            name="Llama 2 34B",
            params=34_000_000_000,
            context_length=4096,
            vocab_size=32000,
            recommended_vram_gb=72,
            training_tflops_days=680,
            finetune_vram_gb=68,
            lora_vram_gb=34,
            qlora_vram_gb=20,
            architecture="LLaMA",
            provider="Meta"
        ),
        "Llama-2-13B": ModelInfo(
            name="Llama 2 13B",
            params=13_000_000_000,
            context_length=4096,
            vocab_size=32000,
            recommended_vram_gb=28,
            training_tflops_days=260,
            finetune_vram_gb=26,
            lora_vram_gb=13,
            qlora_vram_gb=8,
            architecture="LLaMA",
            provider="Meta"
        ),
        "Llama-2-7B": ModelInfo(
            name="Llama 2 7B",
            params=7_000_000_000,
            context_length=4096,
            vocab_size=32000,
            recommended_vram_gb=15,
            training_tflops_days=140,
            finetune_vram_gb=14,
            lora_vram_gb=7,
            qlora_vram_gb=4,
            architecture="LLaMA",
            provider="Meta"
        ),

        # Llama 3 系列
        "Llama-3-70B": ModelInfo(
            name="Llama 3 70B",
            params=70_000_000_000,
            context_length=8192,
            vocab_size=128256,
            recommended_vram_gb=148,
            training_tflops_days=1400,
            finetune_vram_gb=140,
            lora_vram_gb=70,
            qlora_vram_gb=42,
            architecture="LLaMA 3",
            provider="Meta"
        ),
        "Llama-3-8B": ModelInfo(
            name="Llama 3 8B",
            params=8_000_000_000,
            context_length=8192,
            vocab_size=128256,
            recommended_vram_gb=17,
            training_tflops_days=160,
            finetune_vram_gb=16,
            lora_vram_gb=8,
            qlora_vram_gb=5,
            architecture="LLaMA 3",
            provider="Meta"
        ),

        # Mistral 系列
        "Mistral-8x22B": ModelInfo(
            name="Mistral 8x22B",
            params=141_000_000_000,
            context_length=65536,
            vocab_size=200000,
            recommended_vram_gb=296,
            training_tflops_days=2820,
            finetune_vram_gb=282,
            lora_vram_gb=141,
            qlora_vram_gb=85,
            architecture="Mistral",
            provider="Mistral AI"
        ),
        "Mistral-8x7B": ModelInfo(
            name="Mistral 8x7B (Mixtral)",
            params=46_700_000_000,
            context_length=32768,
            vocab_size=32000,
            recommended_vram_gb=98,
            training_tflops_days=934,
            finetune_vram_gb=94,
            lora_vram_gb=47,
            qlora_vram_gb=28,
            architecture="Mixtral",
            provider="Mistral AI"
        ),
        "Mistral-7B": ModelInfo(
            name="Mistral 7B",
            params=7_000_000_000,
            context_length=32768,
            vocab_size=32000,
            recommended_vram_gb=15,
            training_tflops_days=140,
            finetune_vram_gb=14,
            lora_vram_gb=7,
            qlora_vram_gb=4,
            architecture="Mistral",
            provider="Mistral AI"
        ),

        # Qwen 系列
        "Qwen2-72B": ModelInfo(
            name="Qwen2 72B",
            params=72_000_000_000,
            context_length=32768,
            vocab_size=152000,
            recommended_vram_gb=152,
            training_tflops_days=1440,
            finetune_vram_gb=144,
            lora_vram_gb=72,
            qlora_vram_gb=43,
            architecture="Qwen2",
            provider="Alibaba"
        ),
        "Qwen2-57B": ModelInfo(
            name="Qwen2 57B",
            params=57_000_000_000,
            context_length=32768,
            vocab_size=152000,
            recommended_vram_gb=120,
            training_tflops_days=1140,
            finetune_vram_gb=114,
            lora_vram_gb=57,
            qlora_vram_gb=34,
            architecture="Qwen2",
            provider="Alibaba"
        ),
        "Qwen2-7B": ModelInfo(
            name="Qwen2 7B",
            params=7_000_000_000,
            context_length=32768,
            vocab_size=152000,
            recommended_vram_gb=15,
            training_tflops_days=140,
            finetune_vram_gb=14,
            lora_vram_gb=7,
            qlora_vram_gb=4,
            architecture="Qwen2",
            provider="Alibaba"
        ),
        "Qwen1.5-72B": ModelInfo(
            name="Qwen1.5 72B",
            params=72_000_000_000,
            context_length=32768,
            vocab_size=152000,
            recommended_vram_gb=152,
            training_tflops_days=1440,
            finetune_vram_gb=144,
            lora_vram_gb=72,
            qlora_vram_gb=43,
            architecture="Qwen",
            provider="Alibaba"
        ),
        "Qwen1.5-32B": ModelInfo(
            name="Qwen1.5 32B",
            params=32_000_000_000,
            context_length=32768,
            vocab_size=152000,
            recommended_vram_gb=68,
            training_tflops_days=640,
            finetune_vram_gb=64,
            lora_vram_gb=32,
            qlora_vram_gb=19,
            architecture="Qwen",
            provider="Alibaba"
        ),
        "Qwen1.5-14B": ModelInfo(
            name="Qwen1.5 14B",
            params=14_000_000_000,
            context_length=32768,
            vocab_size=152000,
            recommended_vram_gb=30,
            training_tflops_days=280,
            finetune_vram_gb=28,
            lora_vram_gb=14,
            qlora_vram_gb=8,
            architecture="Qwen",
            provider="Alibaba"
        ),
        "Qwen1.5-7B": ModelInfo(
            name="Qwen1.5 7B",
            params=7_000_000_000,
            context_length=32768,
            vocab_size=152000,
            recommended_vram_gb=15,
            training_tflops_days=140,
            finetune_vram_gb=14,
            lora_vram_gb=7,
            qlora_vram_gb=4,
            architecture="Qwen",
            provider="Alibaba"
        ),
        "Qwen1.5-1.8B": ModelInfo(
            name="Qwen1.5 1.8B",
            params=1_800_000_000,
            context_length=32768,
            vocab_size=152000,
            recommended_vram_gb=4,
            training_tflops_days=36,
            finetune_vram_gb=4,
            lora_vram_gb=2,
            qlora_vram_gb=1,
            architecture="Qwen",
            provider="Alibaba"
        ),

        # Baichuan 系列
        "Baichuan2-13B": ModelInfo(
            name="Baichuan2 13B",
            params=13_000_000_000,
            context_length=4096,
            vocab_size=125696,
            recommended_vram_gb=28,
            training_tflops_days=260,
            finetune_vram_gb=26,
            lora_vram_gb=13,
            qlora_vram_gb=8,
            architecture="Baichuan2",
            provider="Baichuan AI"
        ),
        "Baichuan2-7B": ModelInfo(
            name="Baichuan2 7B",
            params=7_000_000_000,
            context_length=4096,
            vocab_size=125696,
            recommended_vram_gb=15,
            training_tflops_days=140,
            finetune_vram_gb=14,
            lora_vram_gb=7,
            qlora_vram_gb=4,
            architecture="Baichuan2",
            provider="Baichuan AI"
        ),

        # ChatGLM 系列
        "ChatGLM4-9B": ModelInfo(
            name="ChatGLM4 9B",
            params=9_000_000_000,
            context_length=128000,
            vocab_size=151551,
            recommended_vram_gb=19,
            training_tflops_days=180,
            finetune_vram_gb=18,
            lora_vram_gb=9,
            qlora_vram_gb=5,
            architecture="ChatGLM4",
            provider="Zhipu AI"
        ),
        "ChatGLM3-6B": ModelInfo(
            name="ChatGLM3 6B",
            params=6_000_000_000,
            context_length=32768,
            vocab_size=64794,
            recommended_vram_gb=13,
            training_tflops_days=120,
            finetune_vram_gb=12,
            lora_vram_gb=6,
            qlora_vram_gb=4,
            architecture="ChatGLM3",
            provider="Zhipu AI"
        ),

        # DeepSeek 系列
        "DeepSeek-V2-236B": ModelInfo(
            name="DeepSeek V2 236B",
            params=236_000_000_000,
            context_length=128000,
            vocab_size=102400,
            recommended_vram_gb=496,
            training_tflops_days=4720,
            finetune_vram_gb=472,
            lora_vram_gb=236,
            qlora_vram_gb=142,
            architecture="DeepSeek V2",
            provider="DeepSeek"
        ),
        "DeepSeek-V2-Lite-16B": ModelInfo(
            name="DeepSeek V2 Lite 16B",
            params=16_000_000_000,
            context_length=128000,
            vocab_size=102400,
            recommended_vram_gb=34,
            training_tflops_days=320,
            finetune_vram_gb=32,
            lora_vram_gb=16,
            qlora_vram_gb=10,
            architecture="DeepSeek V2",
            provider="DeepSeek"
        ),

        # Yi 系列
        "Yi-34B": ModelInfo(
            name="Yi 34B",
            params=34_000_000_000,
            context_length=4096,
            vocab_size=64000,
            recommended_vram_gb=72,
            training_tflops_days=680,
            finetune_vram_gb=68,
            lora_vram_gb=34,
            qlora_vram_gb=20,
            architecture="Yi",
            provider="01.AI"
        ),
        "Yi-6B": ModelInfo(
            name="Yi 6B",
            params=6_000_000_000,
            context_length=4096,
            vocab_size=64000,
            recommended_vram_gb=13,
            training_tflops_days=120,
            finetune_vram_gb=12,
            lora_vram_gb=6,
            qlora_vram_gb=4,
            architecture="Yi",
            provider="01.AI"
        ),

        # Gemma 系列
        "Gemma-2-27B": ModelInfo(
            name="Gemma 2 27B",
            params=27_000_000_000,
            context_length=8192,
            vocab_size=256000,
            recommended_vram_gb=57,
            training_tflops_days=540,
            finetune_vram_gb=54,
            lora_vram_gb=27,
            qlora_vram_gb=16,
            architecture="Gemma 2",
            provider="Google"
        ),
        "Gemma-2-9B": ModelInfo(
            name="Gemma 2 9B",
            params=9_000_000_000,
            context_length=8192,
            vocab_size=256000,
            recommended_vram_gb=19,
            training_tflops_days=180,
            finetune_vram_gb=18,
            lora_vram_gb=9,
            qlora_vram_gb=5,
            architecture="Gemma 2",
            provider="Google"
        ),
        "Gemma-7B": ModelInfo(
            name="Gemma 7B",
            params=7_000_000_000,
            context_length=8192,
            vocab_size=256000,
            recommended_vram_gb=15,
            training_tflops_days=140,
            finetune_vram_gb=14,
            lora_vram_gb=7,
            qlora_vram_gb=4,
            architecture="Gemma",
            provider="Google"
        ),

        # 通用参数规模模型
        "7B": ModelInfo(
            name="7B 模型 (通用)",
            params=7_000_000_000,
            context_length=4096,
            vocab_size=32000,
            recommended_vram_gb=15,
            training_tflops_days=140,
            finetune_vram_gb=14,
            lora_vram_gb=7,
            qlora_vram_gb=4,
            architecture="通用",
            provider="通用"
        ),
        "13B": ModelInfo(
            name="13B 模型 (通用)",
            params=13_000_000_000,
            context_length=4096,
            vocab_size=32000,
            recommended_vram_gb=28,
            training_tflops_days=260,
            finetune_vram_gb=26,
            lora_vram_gb=13,
            qlora_vram_gb=8,
            architecture="通用",
            provider="通用"
        ),
        "33B": ModelInfo(
            name="33B 模型 (通用)",
            params=33_000_000_000,
            context_length=4096,
            vocab_size=32000,
            recommended_vram_gb=70,
            training_tflops_days=660,
            finetune_vram_gb=66,
            lora_vram_gb=33,
            qlora_vram_gb=20,
            architecture="通用",
            provider="通用"
        ),
        "65B": ModelInfo(
            name="65B 模型 (通用)",
            params=65_000_000_000,
            context_length=4096,
            vocab_size=32000,
            recommended_vram_gb=138,
            training_tflops_days=1300,
            finetune_vram_gb=130,
            lora_vram_gb=65,
            qlora_vram_gb=39,
            architecture="通用",
            provider="通用"
        ),
    }

    @classmethod
    def get_model(cls, model_name: str) -> Optional[ModelInfo]:
        """获取模型信息"""
        return cls.Models.get(model_name)

    @classmethod
    def get_all_models(cls) -> List[ModelInfo]:
        """获取所有模型列表"""
        return list(cls.Models.values())

    @classmethod
    def add_custom_model(
        cls,
        name: str,
        params: int,
        context_length: int = 4096,
        vocab_size: int = 32000,
        recommended_vram_gb: float = None,
        finetune_vram_gb: float = None,
        lora_vram_gb: float = None,
        qlora_vram_gb: float = None,
        architecture: str = "自定义",
        provider: str = "自定义"
    ) -> ModelInfo:
        """添加自定义模型"""
        if recommended_vram_gb is None:
            recommended_vram_gb = params / 1_000_000_000 * 2.1
        if finetune_vram_gb is None:
            finetune_vram_gb = params / 1_000_000_000 * 2.0
        if lora_vram_gb is None:
            lora_vram_gb = params / 1_000_000_000 * 1.0
        if qlora_vram_gb is None:
            qlora_vram_gb = params / 1_000_000_000 * 0.6

        model = ModelInfo(
            name=name,
            params=params,
            context_length=context_length,
            vocab_size=vocab_size,
            recommended_vram_gb=recommended_vram_gb,
            training_tflops_days=params / 1_000_000_000 * 20,
            finetune_vram_gb=finetune_vram_gb,
            lora_vram_gb=lora_vram_gb,
            qlora_vram_gb=qlora_vram_gb,
            architecture=architecture,
            provider=provider
        )

        cls.Models[name] = model
        return model


class ComputeEvaluator:
    """
    综合算力评估器
    
    功能:
    1. GPU算力评估 (数据库 + 实时测试)
    2. 模型训练能力评估
    3. 微调能力评估
    4. 自进化能力评估
    """

    def __init__(self, hardware_snapshot: Dict[str, Any]):
        self.snapshot = hardware_snapshot
        self.gpu_info = hardware_snapshot.get("gpu", {})
        self.memory_info = hardware_snapshot.get("memory", {})
        self.cuda_info = hardware_snapshot.get("cuda", {})

    def detect_gpu_model(self) -> str:
        """检测GPU型号"""
        if not self.gpu_info.get("available"):
            return "No GPU"

        devices = self.gpu_info.get("devices", [])
        if devices:
            name = devices[0].get("name", "Unknown")
            return name
        return "Unknown GPU"

    def get_vram_gb(self) -> float:
        """获取显存容量"""
        devices = self.gpu_info.get("devices", [])
        if devices:
            return devices[0].get("memory_total", 0)
        return 0

    def match_gpu_from_database(self) -> Optional[GPUInfo]:
        """从数据库匹配GPU"""
        gpu_name = self.detect_gpu_model()
        return GPUDatabase.match_gpu(gpu_name)

    def benchmark_gpu_real(self, duration_seconds: int = 5) -> Dict[str, float]:
        """
        实时GPU算力基准测试
        
        测试内容:
        1. FP32 GEMM 性能
        2. FP16 GEMM 性能
        3. 显存带宽
        """
        if not TORCH_AVAILABLE:
            return {
                "error": "CUDA not available",
                "fp32_tflops": 0,
                "fp16_tflops": 0,
                "memory_bandwidth_gb_s": 0
            }

        try:
            device = torch.device("cuda")

            # FP32 GEMM 测试
            size = 4096
            iterations = 100

            a_fp32 = torch.randn(size, size, dtype=torch.float32, device=device)
            b_fp32 = torch.randn(size, size, dtype=torch.float32, device=device)

            # 预热
            for _ in range(10):
                _ = torch.matmul(a_fp32, b_fp32)
            torch.cuda.synchronize()

            # 测试
            start = time.time()
            for _ in range(iterations):
                _ = torch.matmul(a_fp32, b_fp32)
            torch.cuda.synchronize()

            fp32_time = time.time() - start
            fp32_flops = 2 * size ** 3 * iterations
            fp32_tflops = fp32_flops / fp32_time / 1e12

            # FP16 GEMM 测试
            a_fp16 = torch.randn(size, size, dtype=torch.float16, device=device)
            b_fp16 = torch.randn(size, size, dtype=torch.float16, device=device)

            # 预热
            for _ in range(10):
                _ = torch.matmul(a_fp16, b_fp16)
            torch.cuda.synchronize()

            # 测试
            start = time.time()
            for _ in range(iterations):
                _ = torch.matmul(a_fp16, b_fp16)
            torch.cuda.synchronize()

            fp16_time = time.time() - start
            fp16_flops = 2 * size ** 3 * iterations
            fp16_tflops = fp16_flops / fp16_time / 1e12

            # 显存带宽测试
            data_size = 256 * 1024 * 1024
            data = torch.randn(data_size, dtype=torch.float32, device=device)

            start = time.time()
            for _ in range(100):
                _ = data.clone()
            torch.cuda.synchronize()

            bandwidth_time = time.time() - start
            bandwidth = (data_size * 4 * 100) / bandwidth_time / 1e9

            return {
                "fp32_tflops": round(fp32_tflops, 2),
                "fp16_tflops": round(fp16_tflops, 2),
                "memory_bandwidth_gb_s": round(bandwidth, 2)
            }

        except Exception as e:
            return {
                "error": str(e),
                "fp32_tflops": 0,
                "fp16_tflops": 0,
                "memory_bandwidth_gb_s": 0
            }

    def estimate_gpu_tflops(self) -> Tuple[float, Dict[str, Any]]:
        """
        综合估算GPU算力 (数据库 + 实时测试)
        
        Returns:
            (估算FP16 Tensor TFLOPS, 详细信息)
        """
        gpu_name = self.detect_gpu_model()
        vram_gb = self.get_vram_gb()

        # 尝试从数据库匹配
        db_gpu = self.match_gpu_from_database()

        if db_gpu:
            # 数据库有数据
            info = {
                "source": "database",
                "gpu_name": gpu_name,
                "matched_gpu": db_gpu.name,
                "fp32_tflops": db_gpu.tflops_fp32,
                "fp16_tflops": db_gpu.tflops_fp16,
                "fp16_tensor_tflops": db_gpu.tflops_fp16_tensor,
                "vram_gb": db_gpu.vram_gb,
                "bandwidth_gb_s": db_gpu.bandwidth_gb_s,
                "architecture": db_gpu.architecture,
            }

            # 如果有实时测试数据，合并
            if TORCH_AVAILABLE and "Unknown" not in gpu_name:
                try:
                    real_benchmark = self.benchmark_gpu_real(duration_seconds=3)
                    if "error" not in real_benchmark:
                        # 计算实际性能相对于理论的比率
                        ratio = real_benchmark["fp16_tflops"] / db_gpu.tflops_fp16 if db_gpu.tflops_fp16 > 0 else 1.0
                        adjusted_tflops = db_gpu.tflops_fp16_tensor * ratio

                        info["source"] = "database + benchmark"
                        info["real_fp16_tflops"] = real_benchmark["fp16_tflops"]
                        info["real_memory_bandwidth"] = real_benchmark["memory_bandwidth_gb_s"]
                        info["performance_ratio"] = round(ratio * 100, 1)
                        info["adjusted_fp16_tensor_tflops"] = round(adjusted_tflops, 2)

                        return adjusted_tflops, info
                except Exception:
                    pass

            return db_gpu.tflops_fp16_tensor, info
        else:
            # 数据库没有，尝试实时测试
            info = {
                "source": "benchmark",
                "gpu_name": gpu_name,
                "vram_gb": vram_gb,
            }

            if TORCH_AVAILABLE:
                try:
                    real_benchmark = self.benchmark_gpu_real(duration_seconds=3)
                    if "error" not in real_benchmark:
                        info["real_fp32_tflops"] = real_benchmark["fp32_tflops"]
                        info["real_fp16_tflops"] = real_benchmark["fp16_tflops"]
                        info["real_memory_bandwidth"] = real_benchmark["memory_bandwidth_gb_s"]
                        return real_benchmark["fp16_tflops"], info
                except Exception:
                    pass

            # 无法确定，返回估算值
            info["source"] = "estimation"
            info["estimation_method"] = "based on VRAM"

            if vram_gb >= 80:
                estimated_tflops = 300.0
            elif vram_gb >= 40:
                estimated_tflops = 150.0
            elif vram_gb >= 24:
                estimated_tflops = 80.0
            elif vram_gb >= 16:
                estimated_tflops = 50.0
            elif vram_gb >= 12:
                estimated_tflops = 40.0
            elif vram_gb >= 8:
                estimated_tflops = 25.0
            else:
                estimated_tflops = 10.0

            return estimated_tflops, info

    def evaluate_pretraining_capability(self, dataset_tokens: int = 100_000_000_000) -> Dict[str, Any]:
        """
        评估预训练能力
        
        Args:
            dataset_tokens: 数据集token数量，默认100B
        """
        tflops, gpu_info = self.estimate_gpu_tflops()
        vram_gb = self.get_vram_gb()

        capable_models = []
        marginal_models = []
        incapable_models = []

        for model_name, model in ModelDatabase.Models.items():
            # 估算训练时间 (假设GPU利用率40%)
            effective_tflops = tflops * 0.4
            estimated_days = (model.training_tflops_days * 1e12) / (effective_tflops * 1e12)

            vram_req = model.recommended_vram_gb

            if vram_req <= vram_gb:
                if estimated_days < 30:
                    capable_models.append({
                        "model_name": model_name,
                        "display_name": model.name,
                        "params_b": model.params / 1e9,
                        "estimated_days": round(estimated_days, 1),
                        "vram_required_gb": round(vram_req, 1),
                        "feasibility": "recommended",
                        "provider": model.provider,
                    })
                else:
                    marginal_models.append({
                        "model_name": model_name,
                        "display_name": model.name,
                        "params_b": model.params / 1e9,
                        "estimated_days": round(estimated_days, 1),
                        "vram_required_gb": round(vram_req, 1),
                        "feasibility": "long_term",
                        "provider": model.provider,
                    })
            else:
                incapable_models.append({
                    "model_name": model_name,
                    "display_name": model.name,
                    "params_b": model.params / 1e9,
                    "vram_required_gb": round(vram_req, 1),
                    "vram_shortage_gb": round(vram_req - vram_gb, 1),
                    "feasibility": "insufficient_vram",
                    "provider": model.provider,
                })

        # 排序
        capable_models.sort(key=lambda x: x["estimated_days"])
        marginal_models.sort(key=lambda x: x["estimated_days"])

        return {
            "gpu_tflops_fp16": round(tflops, 1),
            "gpu_info": gpu_info,
            "vram_gb": round(vram_gb, 1),
            "dataset_tokens": dataset_tokens,
            "capable_models": capable_models[:10],
            "marginal_models": marginal_models[:5],
            "incapable_models": incapable_models[:5],
            "best_choice": capable_models[0] if capable_models else None,
        }

    def evaluate_finetuning_capability(self) -> Dict[str, Any]:
        """评估微调能力"""
        tflops, gpu_info = self.estimate_gpu_tflops()
        vram_gb = self.get_vram_gb()

        results = {
            "full_finetuning": {},
            "lora_finetuning": {},
            "qlora_finetuning": {},
        }

        for model_name, model in ModelDatabase.Models.items():
            # 全参数微调
            vram_full = model.finetune_vram_gb
            results["full_finetuning"][model_name] = {
                "display_name": model.name,
                "params_b": model.params / 1e9,
                "feasible": vram_full <= vram_gb,
                "vram_required_gb": round(vram_full, 1),
                "vram_surplus_gb": round(vram_gb - vram_full, 1) if vram_full <= vram_gb else 0,
                "recommended_gpu": self._recommend_gpu_for_pretraining(vram_full),
                "estimated_training_days": round(model.training_tflops_days * 0.01, 2),
            }

            # LoRA 微调
            vram_lora = model.lora_vram_gb
            results["lora_finetuning"][model_name] = {
                "display_name": model.name,
                "params_b": model.params / 1e9,
                "feasible": vram_lora <= vram_gb,
                "vram_required_gb": round(vram_lora, 1),
                "vram_surplus_gb": round(vram_gb - vram_lora, 1) if vram_lora <= vram_gb else 0,
                "recommended_gpu": self._recommend_gpu_for_pretraining(vram_lora),
                "estimated_training_days": round(model.training_tflops_days * 0.005, 2),
            }

            # QLoRA 微调
            vram_qlora = model.qlora_vram_gb
            results["qlora_finetuning"][model_name] = {
                "display_name": model.name,
                "params_b": model.params / 1e9,
                "feasible": vram_qlora <= vram_gb,
                "vram_required_gb": round(vram_qlora, 1),
                "vram_surplus_gb": round(vram_gb - vram_qlora, 1) if vram_qlora <= vram_gb else 0,
                "recommended_gpu": self._recommend_gpu_for_pretraining(vram_qlora),
                "estimated_training_days": round(model.training_tflops_days * 0.002, 2),
            }

        # 按可行性分组
        feasible_full = [m for m in results["full_finetuning"].values() if m["feasible"]]
        feasible_lora = [m for m in results["lora_finetuning"].values() if m["feasible"]]
        feasible_qlora = [m for m in results["qlora_finetuning"].values() if m["feasible"]]

        return {
            "gpu_tflops_fp16": round(tflops, 1),
            "vram_gb": round(vram_gb, 1),
            "full_finetuning_feasible_count": len(feasible_full),
            "lora_finetuning_feasible_count": len(feasible_lora),
            "qlora_finetuning_feasible_count": len(feasible_qlora),
            "details": results,
            "best_full_model": max(feasible_full, key=lambda x: x["params_b"]) if feasible_full else None,
            "best_lora_model": max(feasible_lora, key=lambda x: x["params_b"]) if feasible_lora else None,
            "best_qlora_model": max(feasible_qlora, key=lambda x: x["params_b"]) if feasible_qlora else None,
        }

    def evaluate_self_improvement_capability(self) -> Dict[str, Any]:
        """评估自进化能力"""
        tflops, gpu_info = self.estimate_gpu_tflops()
        vram_gb = self.get_vram_gb()

        capabilities = {
            "rlhf_training": {
                "name": "强化学习后训练 (RLHF)",
                "description": "使用人类反馈进行强化学习，让模型学习符合人类偏好的行为",
                "feasible": vram_gb >= 24 and tflops >= 50,
                "min_vram_gb": 24,
                "recommended_vram_gb": 40,
                "min_tflops": 50,
                "recommended_tflops": 100,
                "stages": [
                    {"name": "奖励模型训练", "vram_req_gb": 14, "tflops_req": 20, "days": 1},
                    {"name": "PPO训练", "vram_req_gb": 28, "tflops_req": 50, "days": 3},
                ],
                "use_cases": ["对话系统对齐", "代码生成优化", "安全增强"],
                "recommended_model_size": "7B" if vram_gb >= 24 else "不可行",
                "estimated_total_days": 4,
            },
            "knowledge_distillation": {
                "name": "知识蒸馏 (Knowledge Distillation)",
                "description": "将大模型的知识迁移到小模型，实现模型压缩和加速",
                "feasible": vram_gb >= 16 and tflops >= 30,
                "min_vram_gb": 16,
                "recommended_vram_gb": 40,
                "min_tflops": 30,
                "recommended_tflops": 80,
                "stages": [
                    {"name": "教师模型推理", "vram_req_gb": 28, "tflops_req": 50, "days": 1},
                    {"name": "学生模型训练", "vram_req_gb": 8, "tflops_req": 20, "days": 1},
                ],
                "use_cases": ["模型压缩", "边缘部署", "实时推理"],
                "recommended_model_size": "7B→2B" if vram_gb >= 24 else "4B→1B",
                "estimated_total_days": 2,
            },
            "continual_learning": {
                "name": "持续预训练 (Continual Pre-training)",
                "description": "在原有模型基础上继续训练，让模型学习新知识和能力",
                "feasible": vram_gb >= 16 and tflops >= 30,
                "min_vram_gb": 16,
                "recommended_vram_gb": 40,
                "min_tflops": 30,
                "recommended_tflops": 80,
                "stages": [
                    {"name": "领域适应训练", "vram_req_gb": 14, "tflops_req": 40, "days": 2},
                    {"name": "知识注入", "vram_req_gb": 14, "tflops_req": 40, "days": 3},
                ],
                "use_cases": ["领域适应", "知识更新", "能力增强"],
                "recommended_model_size": "13B" if vram_gb >= 24 else "7B",
                "estimated_total_days": 5,
            },
            "self_improvement_loop": {
                "name": "自我改进循环 (Self-Improvement)",
                "description": "让模型自己生成、评估和改进解决方案，实现自主进化",
                "feasible": vram_gb >= 80 and tflops >= 300,
                "min_vram_gb": 80,
                "recommended_vram_gb": 160,
                "min_tflops": 300,
                "recommended_tflops": 600,
                "stages": [
                    {"name": "候选生成", "vram_req_gb": 56, "tflops_req": 150, "days": 1},
                    {"name": "自我评估", "vram_req_gb": 56, "tflops_req": 150, "days": 1},
                    {"name": "策略优化", "vram_req_gb": 56, "tflops_req": 150, "days": 2},
                ],
                "use_cases": ["复杂问题解决", "科学研究", "自主代理"],
                "recommended_model_size": "需要多卡配置 (8xA100)",
                "estimated_total_days": 10,
                "note": "⚠️ 需要复杂的多阶段系统和大量计算资源",
            },
            "in_context_learning": {
                "name": "上下文学习优化 (ICL Optimization)",
                "description": "自动优化提示和上下文示例，提升模型的few-shot学习能力",
                "feasible": vram_gb >= 8 and tflops >= 15,
                "min_vram_gb": 8,
                "recommended_vram_gb": 16,
                "min_tflops": 15,
                "recommended_tflops": 40,
                "stages": [
                    {"name": "示例搜索", "vram_req_gb": 7, "tflops_req": 15, "days": 0.5},
                    {"name": "提示优化", "vram_req_gb": 7, "tflops_req": 20, "days": 0.5},
                ],
                "use_cases": ["Few-shot学习", "提示工程自动化", "任务适配"],
                "recommended_model_size": "13B" if vram_gb >= 24 else "7B",
                "estimated_total_days": 1,
            },
            "model_ensemble": {
                "name": "模型集成 (Model Ensemble)",
                "description": "组合多个模型的预测结果，提升整体性能",
                "feasible": vram_gb >= 32 and tflops >= 60,
                "min_vram_gb": 32,
                "recommended_vram_gb": 80,
                "min_tflops": 60,
                "recommended_tflops": 150,
                "stages": [
                    {"name": "多模型训练", "vram_req_gb": 14, "tflops_req": 50, "days": 3},
                    {"name": "集成优化", "vram_req_gb": 28, "tflops_req": 80, "days": 1},
                ],
                "use_cases": ["性能提升", "不确定性估计", "鲁棒性增强"],
                "recommended_model_size": "多个7B" if vram_gb >= 24 else "多个1B",
                "estimated_total_days": 4,
            },
        }

        # 计算每个能力的可行性评分
        for cap_name, cap in capabilities.items():
            score = 0

            # 显存评分
            if vram_gb >= cap["recommended_vram_gb"]:
                score += 40
            elif vram_gb >= cap["min_vram_gb"]:
                score += 20
            else:
                score -= 20

            # 算力评分
            if tflops >= cap["recommended_tflops"]:
                score += 40
            elif tflops >= cap["min_tflops"]:
                score += 20
            else:
                score -= 20

            # 多GPU支持评分
            if vram_gb >= 80:
                score += 20

            cap["feasibility_score"] = min(100, max(0, score))
            cap["feasibility_label"] = (
                "recommended" if score >= 70
                else "marginal" if score >= 40
                else "not_recommended"
            )

        return {
            "gpu_tflops_fp16": round(tflops, 1),
            "vram_gb": round(vram_gb, 1),
            "capabilities": capabilities,
            "recommended_capabilities": [
                cap for cap in capabilities.values()
                if cap["feasibility_label"] == "recommended"
            ],
        }

    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """生成综合算力评估报告"""
        pretrain = self.evaluate_pretraining_capability()
        finetune = self.evaluate_finetuning_capability()
        self_improve = self.evaluate_self_improvement_capability()

        gpu_name = self.detect_gpu_model()
        tflops = pretrain["gpu_tflops_fp16"]
        vram_gb = pretrain["vram_gb"]

        # 生成综合建议
        recommendations = []

        if finetune["best_qlora_model"]:
            recommendations.append({
                "type": "immediate",
                "title": "立即可执行: QLoRA微调",
                "description": f"您可以使用QLoRA微调 {finetune['best_qlora_model']['display_name']}",
                "action": "start_qlora_training",
                "priority": "high"
            })

        if finetune["best_lora_model"]:
            recommendations.append({
                "type": "recommended",
                "title": "推荐: LoRA微调",
                "description": f"建议使用LoRA微调 {finetune['best_lora_model']['display_name']}",
                "action": "start_lora_training",
                "priority": "medium"
            })

        if self_improve["recommended_capabilities"]:
            best_cap = self_improve["recommended_capabilities"][0]
            recommendations.append({
                "type": "advanced",
                "title": f"高级: {best_cap['name']}",
                "description": f"您具备执行 {best_cap['name']} 的能力",
                "action": "explore_advanced",
                "priority": "low"
            })

        # 升级建议
        upgrade_recommendations = []

        if vram_gb < 24:
            upgrade_recommendations.append({
                "current": f"RTX 3080 ({vram_gb}GB)",
                "target": "RTX 4090 (24GB)",
                "improvement": "显存翻倍，可全参数微调13B模型",
                "priority": "high"
            })

        if tflops < 80:
            upgrade_recommendations.append({
                "current": f"当前GPU ({tflops} TFLOPS)",
                "target": "RTX 4090 (165 TFLOPS)",
                "improvement": "算力提升2.8倍，训练速度大幅提升",
                "priority": "high"
            })

        if vram_gb < 80 and tflops < 200:
            upgrade_recommendations.append({
                "current": "当前配置",
                "target": "A100 40GB (312 TFLOPS)",
                "improvement": "专业级GPU，可训练70B模型",
                "priority": "medium"
            })

        return {
            "timestamp": datetime.now().isoformat(),
            "gpu_info": {
                "model": gpu_name,
                "tflops_fp16": tflops,
                "vram_gb": vram_gb,
            },
            "pretraining_assessment": pretrain,
            "finetuning_assessment": finetune,
            "self_improvement_assessment": self_improve,
            "recommendations": recommendations,
            "upgrade_recommendations": upgrade_recommendations,
            "overall_score": self._calculate_overall_score(tflops, vram_gb),
        }

    def _recommend_gpu_for_pretraining(self, vram_required_gb: float) -> str:
        """推荐满足显存需求的GPU"""
        for gpu_name, gpu in sorted(GPUDatabase.GPUs.items(), key=lambda x: x[1].vram_gb):
            if gpu.vram_gb >= vram_required_gb:
                return f"{gpu.name} ({gpu.vram_gb}GB)"
        return "需要多GPU配置"

    def _calculate_overall_score(self, tflops: float, vram_gb: float) -> Dict[str, Any]:
        """计算综合评分"""
        # 算力评分 (满分40分)
        if tflops >= 300:
            compute_score = 40
        elif tflops >= 150:
            compute_score = 30
        elif tflops >= 80:
            compute_score = 25
        elif tflops >= 40:
            compute_score = 20
        elif tflops >= 20:
            compute_score = 15
        else:
            compute_score = 10

        # 显存评分 (满分40分)
        if vram_gb >= 80:
            memory_score = 40
        elif vram_gb >= 40:
            memory_score = 30
        elif vram_gb >= 24:
            memory_score = 25
        elif vram_gb >= 16:
            memory_score = 20
        elif vram_gb >= 8:
            memory_score = 15
        else:
            memory_score = 5

        # 多GPU支持 (满分20分)
        multi_gpu_score = 0
        if vram_gb >= 80:
            multi_gpu_score = 20
        elif vram_gb >= 40:
            multi_gpu_score = 15
        elif vram_gb >= 24:
            multi_gpu_score = 10

        total_score = compute_score + memory_score + multi_gpu_score

        return {
            "total": total_score,
            "compute_score": compute_score,
            "memory_score": memory_score,
            "multi_gpu_score": multi_gpu_score,
            "grade": (
                "S" if total_score >= 90
                else "A" if total_score >= 75
                else "B" if total_score >= 60
                else "C" if total_score >= 40
                else "D"
            ),
            "description": (
                "专业级 AI 训练平台" if total_score >= 90
                else "企业级 AI 训练平台" if total_score >= 75
                else "高性能个人 AI 工作站" if total_score >= 60
                else "入门级 AI 训练平台" if total_score >= 40
                else "受限 AI 学习平台"
            )
        }

    def get_gpu_ranking(self) -> List[Dict[str, Any]]:
        """获取GPU排名"""
        user_tflops, _ = self.estimate_gpu_tflops()
        user_vram = self.get_vram_gb()
        user_name = self.detect_gpu_model()

        rankings = []

        for gpu_name, gpu in GPUDatabase.GPUs.items():
            tflops_ratio = (gpu.tflops_fp16_tensor / user_tflops * 100) if user_tflops > 0 else 0
            vram_ratio = (gpu.vram_gb / user_vram * 100) if user_vram > 0 else 0

            rankings.append({
                "gpu_name": gpu.name,
                "tflops_fp16": gpu.tflops_fp16_tensor,
                "vram_gb": gpu.vram_gb,
                "architecture": gpu.architecture,
                "tflops_vs_user": round(tflops_ratio, 1),
                "vram_vs_user": round(vram_ratio, 1),
                "is_user_gpu": user_name.lower() in gpu_name.lower() or gpu_name.lower() in user_name.lower(),
            })

        # 按算力排序
        rankings.sort(key=lambda x: x["tflops_fp16"], reverse=True)

        # 添加排名
        for i, gpu in enumerate(rankings):
            gpu["rank"] = i + 1

        return rankings
