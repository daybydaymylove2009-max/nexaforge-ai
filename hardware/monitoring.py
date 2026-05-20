#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智核万炼® NexaForge AI - 监控和指标模块
NexaForge AI Monitoring and Metrics
"""

from prometheus_fastapi_instrumentator import Instrumentator, metrics
from prometheus_fastapi_instrumentator.metrics import Info
from fastapi import FastAPI, Request
from fastapi.responses import Response
import time


def create_instrumentator() -> Instrumentator:
    """创建 Prometheus 监控仪表"""
    instrumentator = Instrumentator(
        should_group_status_codes=False,
        should_ignore_untemplated=True,
        should_respect_env_var=True,
        should_instrument_requests_inprogress=True,
        excluded_handlers=["/metrics", "/health", "/health/ready", "/health/live"],
        inprogress_name="http_requests_inprogress",
        inprogress_labels=True,
    )

    # 添加标准指标
    instrumentator.add(
        metrics.default(
            metric_namespace="nexaforge",
            metric_subsystem="api",
        )
    )

    # 添加请求时长指标
    instrumentator.add(
        metrics.request_size(
            metric_namespace="nexaforge",
            metric_subsystem="api",
        )
    )

    # 添加响应大小指标
    instrumentator.add(
        metrics.response_size(
            metric_namespace="nexaforge",
            metric_subsystem="api",
        )
    )

    # 添加业务指标
    instrumentator.add(hardware_metrics())

    return instrumentator


def hardware_metrics() -> Info:
    """自定义硬件监控指标"""

    def instrumentation(info):
        try:
            from hardware.detector import detector

            # 添加硬件健康指标
            if hasattr(detector, 'last_snapshot'):
                snapshot = detector.last_snapshot
                if snapshot and isinstance(snapshot, dict):
                    cpu_percent = snapshot.get("cpu", {}).get("percent", 0)
                    memory_percent = snapshot.get("memory", {}).get("percent", 0)

                    info.labels(
                        cpu_percent=cpu_percent,
                        memory_percent=memory_percent
                    )
        except Exception:
            pass

    return Info(
        "hardware_metrics",
        "Hardware monitoring metrics",
        instrumentation=instrumentation,
    )
