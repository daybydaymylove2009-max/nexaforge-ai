#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智核万炼® NexaForge AI - 重试机制模块
NexaForge AI Retry Mechanism
"""

import functools
import logging
import time
from typing import Callable, Any
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
    after_log
)

logger = logging.getLogger("NexaForge.Retry")


def retry_on_failure(
    max_attempts: int = 3,
    min_wait: float = 1.0,
    max_wait: float = 10.0,
    exceptions: tuple = (Exception,)
) -> Callable:
    """
    重试装饰器

    Args:
        max_attempts: 最大重试次数
        min_wait: 最小等待时间（秒）
        max_wait: 最大等待时间（秒）
        exceptions: 需要重试的异常类型
    """
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=1, min=min_wait, max=max_wait),
        retry=retry_if_exception_type(exceptions),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        after=after_log(logger, logging.INFO),
        reraise=True
    )


def retry_with_fallback(default: Any = None, max_attempts: int = 2):
    """
    带降级策略的重试装饰器

    Args:
        default: 重试失败后返回的默认值
        max_attempts: 最大重试次数
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.warning(f"函数 {func.__name__} 执行失败: {e}")
                for attempt in range(1, max_attempts):
                    try:
                        logger.info(f"第 {attempt} 次重试...")
                        return func(*args, **kwargs)
                    except Exception as retry_error:
                        logger.warning(f"第 {attempt} 次重试失败: {retry_error}")
                        if attempt == max_attempts - 1:
                            logger.error(f"函数 {func.__name__} 重试 {max_attempts} 次后失败，返回默认值")
                            return default
                return default
        return wrapper
    return decorator


class CircuitBreaker:
    """断路器模式 - 防止级联故障"""

    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """执行函数，带断路器保护"""
        if self.state == "open":
            if self._should_attempt_reset():
                self.state = "half-open"
                logger.info("断路器进入半开状态")
            else:
                raise Exception("断路器已打开，拒绝请求")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e

    def _on_success(self):
        """成功时的处理"""
        self.failure_count = 0
        if self.state == "half-open":
            self.state = "closed"
            logger.info("断路器已关闭，服务恢复正常")

    def _on_failure(self):
        """失败时的处理"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = "open"
            logger.error(f"断路器已打开，连续 {self.failure_count} 次失败")

    def _should_attempt_reset(self) -> bool:
        """检查是否应该尝试重置断路器"""
        if self.last_failure_time is None:
            return True
        return (time.time() - self.last_failure_time) >= self.recovery_timeout


class RateLimiter:
    """简单的速率限制器"""

    def __init__(self, max_calls: int, time_window: float):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []

    def is_allowed(self) -> bool:
        """检查是否允许调用"""
        now = time.time()
        self.calls = [call_time for call_time in self.calls if now - call_time < self.time_window]

        if len(self.calls) < self.max_calls:
            self.calls.append(now)
            return True
        return False

    def wait_time(self) -> float:
        """获取需要等待的时间"""
        if not self.calls:
            return 0
        now = time.time()
        oldest = min(self.calls)
        return max(0, self.time_window - (now - oldest))
