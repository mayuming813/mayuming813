#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : retry_helper.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : 
"""
import time
import functools
from typing import Callable, Any
import allure


def retry_on_failure(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    失败重试装饰器
    :param max_retries: 最大重试次数
    :param delay: 初始延迟时间（秒）
    :param backoff: 延迟时间倍数（指数退避）
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            current_delay = delay
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    if attempt > 0:
                        with allure.step(f"🔄 重试第 {attempt} 次，延迟 {current_delay:.1f}s"):
                            time.sleep(current_delay)
                            current_delay *= backoff

                    result = func(*args, **kwargs)

                    if attempt > 0:
                        with allure.step(f"✅ 重试成功（第 {attempt} 次）"):
                            pass

                    return result

                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        with allure.step(f"❌ 第 {attempt + 1} 次执行失败: {str(e)}"):
                            pass
                    else:
                        with allure.step(f"❌ 重试 {max_retries} 次后仍失败"):
                            pass

            raise last_exception

        return wrapper
    return decorator


class RetryHelper:
    """重试辅助类"""

    @staticmethod
    def retry_until_success(
        func: Callable,
        max_retries: int = 3,
        delay: float = 1.0,
        backoff: float = 2.0,
        *args,
        **kwargs
    ) -> Any:
        """
        重试直到成功
        :param func: 要执行的函数
        :param max_retries: 最大重试次数
        :param delay: 初始延迟时间
        :param backoff: 延迟时间倍数
        :return: 函数执行结果
        """
        current_delay = delay
        last_exception = None

        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    time.sleep(current_delay)
                    current_delay *= backoff

                return func(*args, **kwargs)

            except Exception as e:
                last_exception = e
                if attempt >= max_retries:
                    raise

        raise last_exception

    @staticmethod
    def retry_with_condition(
        func: Callable,
        condition: Callable[[Any], bool],
        max_retries: int = 3,
        delay: float = 1.0,
        *args,
        **kwargs
    ) -> Any:
        """
        重试直到满足条件
        :param func: 要执行的函数
        :param condition: 条件判断函数，返回True表示成功
        :param max_retries: 最大重试次数
        :param delay: 延迟时间
        :return: 函数执行结果
        """
        for attempt in range(max_retries + 1):
            if attempt > 0:
                time.sleep(delay)

            result = func(*args, **kwargs)

            if condition(result):
                return result

            if attempt >= max_retries:
                raise TimeoutError(f"重试 {max_retries} 次后仍未满足条件")

        return result
