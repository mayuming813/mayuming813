#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : polling_helper.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : 
"""
import time
from typing import Callable, Any, Optional
import allure


class PollingHelper:
    """异步轮询辅助类"""

    @staticmethod
    def poll_until_success(
        func: Callable,
        condition: Callable[[Any], bool],
        timeout: float = 60.0,
        interval: float = 2.0,
        *args,
        **kwargs
    ) -> Any:
        """
        轮询直到成功
        :param func: 要执行的函数
        :param condition: 条件判断函数，返回True表示成功
        :param timeout: 超时时间（秒）
        :param interval: 轮询间隔（秒）
        :return: 函数执行结果
        """
        start_time = time.time()
        attempt = 0

        while True:
            attempt += 1
            elapsed = time.time() - start_time

            with allure.step(f"🔍 轮询第 {attempt} 次（已耗时 {elapsed:.1f}s）"):
                try:
                    result = func(*args, **kwargs)

                    if condition(result):
                        with allure.step(f"✅ 轮询成功（共 {attempt} 次，耗时 {elapsed:.1f}s）"):
                            pass
                        return result
                    else:
                        with allure.step(f"⏳ 条件未满足，继续轮询"):
                            pass

                except Exception as e:
                    with allure.step(f"⚠️ 轮询异常: {str(e)}"):
                        pass

            if elapsed >= timeout:
                raise TimeoutError(
                    f"轮询超时（{timeout}s），共尝试 {attempt} 次"
                )

            time.sleep(interval)

    @staticmethod
    def poll_until_value(
        func: Callable,
        expected_value: Any,
        timeout: float = 60.0,
        interval: float = 2.0,
        *args,
        **kwargs
    ) -> Any:
        """
        轮询直到返回期望值
        :param func: 要执行的函数
        :param expected_value: 期望值
        :param timeout: 超时时间
        :param interval: 轮询间隔
        :return: 函数执行结果
        """
        def condition(result):
            return result == expected_value

        return PollingHelper.poll_until_success(
            func, condition, timeout, interval, *args, **kwargs
        )

    @staticmethod
    def poll_until_not_none(
        func: Callable,
        timeout: float = 60.0,
        interval: float = 2.0,
        *args,
        **kwargs
    ) -> Any:
        """
        轮询直到返回非None值
        :param func: 要执行的函数
        :param timeout: 超时时间
        :param interval: 轮询间隔
        :return: 函数执行结果
        """
        def condition(result):
            return result is not None

        return PollingHelper.poll_until_success(
            func, condition, timeout, interval, *args, **kwargs
        )

    @staticmethod
    def poll_transaction_receipt(
        get_receipt_func: Callable[[str], Any],
        tx_hash: str,
        timeout: float = 120.0,
        interval: float = 3.0
    ) -> Any:
        """
        轮询交易回执（专用于区块链交易）
        :param get_receipt_func: 获取交易回执的函数
        :param tx_hash: 交易哈希
        :param timeout: 超时时间
        :param interval: 轮询间隔
        :return: 交易回执
        """
        with allure.step(f"⏳ 等待交易确认: {tx_hash}"):
            def condition(receipt):
                # 交易回执存在且不为None
                return receipt is not None

            return PollingHelper.poll_until_success(
                get_receipt_func,
                condition,
                timeout,
                interval,
                tx_hash
            )

    @staticmethod
    def poll_with_validator(
        func: Callable,
        validator: Callable[[Any], tuple[bool, Optional[str]]],
        timeout: float = 60.0,
        interval: float = 2.0,
        *args,
        **kwargs
    ) -> Any:
        """
        轮询并使用验证器
        :param func: 要执行的函数
        :param validator: 验证器函数，返回 (是否成功, 错误信息)
        :param timeout: 超时时间
        :param interval: 轮询间隔
        :return: 函数执行结果
        """
        start_time = time.time()
        attempt = 0

        while True:
            attempt += 1
            elapsed = time.time() - start_time

            with allure.step(f"🔍 轮询第 {attempt} 次（已耗时 {elapsed:.1f}s）"):
                try:
                    result = func(*args, **kwargs)
                    is_valid, error_msg = validator(result)

                    if is_valid:
                        with allure.step(f"✅ 验证通过（共 {attempt} 次，耗时 {elapsed:.1f}s）"):
                            pass
                        return result
                    else:
                        with allure.step(f"⏳ 验证未通过: {error_msg or '条件未满足'}"):
                            pass

                except Exception as e:
                    with allure.step(f"⚠️ 轮询异常: {str(e)}"):
                        pass

            if elapsed >= timeout:
                raise TimeoutError(
                    f"轮询超时（{timeout}s），共尝试 {attempt} 次"
                )

            time.sleep(interval)
