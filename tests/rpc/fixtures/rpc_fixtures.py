#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : rpc_fixtures.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : 
"""
import pytest
import allure
import json
from tests.rpc.rpcs.blockchain_rpc import BlockchainRPC
from tests.rpc.rpcs.contract_rpc import ContractRPC
from framework.utils.rpc_client import RPCClient
from framework.utils.rpc_validator import RPCValidator
from framework.utils.test_data_factory import TestDataFactory
from framework.utils.polling_helper import PollingHelper
from framework.utils.retry_helper import retry_on_failure
from framework.core.config import config


# ==================== Allure 报告增强 ====================

def attach_rpc_request(method: str, params: list = None):
    """附加 RPC 请求信息"""
    request_info = {
        'method': method,
        'params': params or []
    }
    allure.attach(
        json.dumps(request_info, indent=2, ensure_ascii=False),
        name="📤 RPC 请求",
        attachment_type=allure.attachment_type.JSON
    )


def attach_rpc_response(response):
    """附加 RPC 响应信息"""
    try:
        response_data = response.json()
    except:
        response_data = {'raw': response.text}

    allure.attach(
        json.dumps(response_data, indent=2, ensure_ascii=False),
        name="📥 RPC 响应",
        attachment_type=allure.attachment_type.JSON
    )


def attach_rpc_step(step_name: str, **data):
    """附加 RPC 步骤信息"""
    allure.attach(
        json.dumps(data, indent=2, ensure_ascii=False),
        name=f"📝 {step_name}",
        attachment_type=allure.attachment_type.JSON
    )


# ==================== 基础 Fixtures ====================

@pytest.fixture(scope="function")
def rpc_client():
    """RPC 客户端 fixture"""
    client = RPCClient(rpc_url=config.rpc_url)
    yield client
    client.close()


@pytest.fixture(scope="function")
def blockchain_rpc(rpc_client):
    """区块链 RPC fixture"""
    return BlockchainRPC(client=rpc_client)


@pytest.fixture(scope="function")
def contract_rpc(rpc_client):
    """合约 RPC fixture"""
    return ContractRPC(client=rpc_client)


@pytest.fixture(scope="function")
def rpc_validator():
    """RPC 验证器 fixture"""
    return RPCValidator()


@pytest.fixture(scope="function")
def test_data():
    """测试数据工厂 fixture"""
    return TestDataFactory()


@pytest.fixture(scope="function")
def polling_helper():
    """轮询辅助工具 fixture"""
    return PollingHelper()


# ==================== 场景 Fixtures ====================

@pytest.fixture(scope="function")
@retry_on_failure(max_retries=3, delay=1.0, backoff=2.0)
def latest_block(blockchain_rpc, rpc_validator):
    """
    场景模块：获取最新区块（带重试）
    返回：区块号和区块信息
    """
    with allure.step("获取最新区块号"):
        response = blockchain_rpc.get_block_number()
        attach_rpc_request("eth_blockNumber")
        attach_rpc_response(response)

        assert rpc_validator.validate_rpc_response(response), \
            f"获取区块号失败: {response.status_code}"

        block_number = rpc_validator.extract_rpc_result(response)
        assert block_number, "区块号为空"

    with allure.step("获取区块详情"):
        response = blockchain_rpc.get_block_by_number(block_number, False)
        attach_rpc_request("eth_getBlockByNumber", [block_number, False])
        attach_rpc_response(response)

        assert rpc_validator.validate_rpc_response(response), \
            f"获取区块详情失败: {response.status_code}"

        block_info = rpc_validator.extract_rpc_result(response)

    return {
        'block_number': block_number,
        'block_info': block_info
    }


@pytest.fixture(scope="function")
def transaction_with_receipt(blockchain_rpc, rpc_validator, polling_helper, test_data):
    """
    场景模块：发送交易并轮询获取回执
    返回：交易哈希和回执
    """
    # 注意：这是示例，实际需要有效的签名交易
    tx_hash = "0x" + test_data.unique_id()

    with allure.step("轮询交易回执"):
        def get_receipt(hash):
            response = blockchain_rpc.get_transaction_receipt(hash)
            if rpc_validator.validate_rpc_response(response):
                return rpc_validator.extract_rpc_result(response)
            return None

        try:
            receipt = polling_helper.poll_transaction_receipt(
                get_receipt,
                tx_hash,
                timeout=config.get('polling.transaction_timeout', 120.0),
                interval=config.get('polling.transaction_interval', 3.0)
            )
        except TimeoutError:
            # 示例场景，允许超时
            receipt = None

    return {
        'tx_hash': tx_hash,
        'receipt': receipt
    }

