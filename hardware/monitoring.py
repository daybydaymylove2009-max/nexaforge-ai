#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NexaForge AI - Monitoring and Metrics Module
"""

from prometheus_fastapi_instrumentator import Instrumentator, metrics
from fastapi import FastAPI, Request
from fastapi.responses import Response
import time


def create_instrumentator() -> Instrumentator:
    instrumentator = Instrumentator(
        should_group_status_codes=False,
        should_ignore_untemplated=True,
        should_respect_env_var=False,
        should_instrument_requests_inprogress=True,
        excluded_handlers=["/metrics", "/health", "/health/ready", "/health/live"],
        inprogress_name="http_requests_inprogress",
        inprogress_labels=True,
    )

    instrumentator.add(
        metrics.default(
            metric_namespace="nexaforge",
            metric_subsystem="api",
        )
    )

    instrumentator.add(
        metrics.request_size(
            metric_namespace="nexaforge",
            metric_subsystem="api",
        )
    )

    instrumentator.add(
        metrics.response_size(
            metric_namespace="nexaforge",
            metric_subsystem="api",
        )
    )

    return instrumentator
