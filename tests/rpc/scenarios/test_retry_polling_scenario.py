#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : test_retry_polling_scenario.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : 
"""
import pytest
import allure
from tests.rpc.fixtures.rpc_fixtures import attach_rpc_request, attach_rpc_response, attach_rpc_step
from framework.utils.retry_helper import retry_on_failure, RetryHelper
from framework.utils.polling_helper import PollingHelper
from framework.core.config import config


@allure.feature("重试和轮询能力")
@allure.story("重试机制")
class TestRetryScenario:
    """重试机制示例"""

    @allure.title("场景：使用装饰器重试查询区块")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("使用 @retry_on_failure 装饰器自动重试")
    @retry_on_failure(
        max_retries=config.get('retry.max_retries', 3),
        delay=config.get('retry.delay', 1.0),
        backoff=config.get('retry.backoff', 2.0)
    )
    def test_retry_with_decorator(self, blockchain_rpc, rpc_validator):
        """
        场景：使用装饰器重试
        """
        with allure.step("查询最新区块号（带重试）"):
            response = blockchain_rpc.get_block_number()
            attach_rpc_response(response)

            assert rpc_validator.validate_rpc_response(response), \
                f"查询失败: {response.status_code}"

            block_number = rpc_validator.extract_rpc_result(response)
            assert block_number, "区块号为空"

    @allure.title("场景：使用 RetryHelper 重试")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("使用 RetryHelper 类手动控制重试")
    def test_retry_with_helper(self, blockchain_rpc, rpc_validator):
        """
        场景：使用 RetryHelper 重试
        """
        with allure.step("使用 RetryHelper 查询余额"):
            def query_balance():
                address = "0x0000000000000000000000000000000000000000"
                response = blockchain_rpc.get_balance(address)
                attach_rpc_response(response)

                if not rpc_validator.validate_rpc_response(response):
                    raise Exception(f"查询失败: {response.status_code}")

                return rpc_validator.extract_rpc_result(response)

            balance = RetryHelper.retry_until_success(
                query_balance,
                max_retries=config.get('retry.max_retries', 3),
                delay=config.get('retry.delay', 1.0),
                backoff=config.get('retry.backoff', 2.0)
            )

            attach_rpc_step("余额查询结果", balance=balance)


@allure.feature("重试和轮询能力")
@allure.story("轮询机制")
class TestPollingScenario:
    """轮询机制示例"""

    @allure.title("场景：轮询交易回执")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("轮询等待交易确认")
    def test_poll_transaction_receipt(self, transaction_with_receipt):
        """
        场景：轮询交易回执
        使用 fixture：transaction_with_receipt
        """
        tx_hash = transaction_with_receipt['tx_hash']
        receipt = transaction_with_receipt['receipt']

        attach_rpc_step("交易信息", tx_hash=tx_hash, has_receipt=receipt is not None)

    @allure.title("场景：轮询直到满足条件")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("轮询直到区块号增长")
    def test_poll_until_condition(self, blockchain_rpc, rpc_validator):
        """
        场景：轮询直到条件满足
        """
        with allure.step("获取初始区块号"):
            response = blockchain_rpc.get_block_number()
            initial_block = rpc_validator.extract_rpc_result(response)
            initial_block_int = int(initial_block, 16) if initial_block else 0

        with allure.step("轮询等待新区块"):
            def get_current_block():
                response = blockchain_rpc.get_block_number()
                if rpc_validator.validate_rpc_response(response):
                    return rpc_validator.extract_rpc_result(response)
                return None

            def is_new_block(block_hex):
                if not block_hex:
                    return False
                current_int = int(block_hex, 16)
                return current_int > initial_block_int

            try:
                new_block = PollingHelper.poll_until_success(
                    get_current_block,
                    is_new_block,
                    timeout=30.0,
                    interval=2.0
                )
                attach_rpc_step("新区块", initial=initial_block, new=new_block)
            except TimeoutError as e:
                # 在测试环境可能不会产生新区块，允许超时
                attach_rpc_step("轮询超时", message=str(e))

    @allure.title("场景：轮询直到非空值")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("轮询直到获取到有效数据")
    def test_poll_until_not_none(self, blockchain_rpc, rpc_validator):
        """
        场景：轮询直到非空
        """
        with allure.step("轮询获取区块号"):
            def get_block_number():
                response = blockchain_rpc.get_block_number()
                if rpc_validator.validate_rpc_response(response):
                    return rpc_validator.extract_rpc_result(response)
                return None

            block_number = PollingHelper.poll_until_not_none(
                get_block_number,
                timeout=config.get('polling.timeout', 60.0),
                interval=config.get('polling.interval', 2.0)
            )

            attach_rpc_step("区块号", block_number=block_number)

    @allure.title("场景：使用验证器轮询")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("轮询并使用自定义验证器")
    def test_poll_with_validator(self, blockchain_rpc, rpc_validator):
        """
        场景：使用验证器轮询
        """
        with allure.step("轮询并验证区块号格式"):
            def get_block_number():
                response = blockchain_rpc.get_block_number()
                if rpc_validator.validate_rpc_response(response):
                    return rpc_validator.extract_rpc_result(response)
                return None

            def validate_block_format(block_hex):
                """验证区块号格式"""
                if not block_hex:
                    return False, "区块号为空"
                if not block_hex.startswith('0x'):
                    return False, "区块号格式错误：缺少0x前缀"
                try:
                    int(block_hex, 16)
                    return True, None
                except ValueError:
                    return False, "区块号格式错误：不是有效的十六进制"

            block_number = PollingHelper.poll_with_validator(
                get_block_number,
                validate_block_format,
                timeout=30.0,
                interval=1.0
            )

            attach_rpc_step("验证通过", block_number=block_number)
