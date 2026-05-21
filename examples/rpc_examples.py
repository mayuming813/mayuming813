#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : rpc_examples.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : RPC 测试完整示例
"""
import pytest
import allure
from tests.rpc.rpcs.blockchain_rpc import BlockchainRPC
from tests.rpc.rpcs.contract_rpc import ContractRPC
from framework.utils.rpc_client import RPCClient
from framework.utils.rpc_validator import RPCValidator
from framework.utils.test_data_factory import TestDataFactory
from framework.utils.polling_helper import PollingHelper
from framework.core.config import config


# ==================== 单接口测试示例 ====================

@allure.feature("RPC 单接口测试")
@allure.story("区块链基础接口")
class TestBlockchainRPCExamples:
    """区块链 RPC 单接口测试示例"""

    def test_get_block_number(self, blockchain_rpc, rpc_validator):
        """示例：获取最新区块号"""
        with allure.step("调用 eth_blockNumber"):
            response = blockchain_rpc.get_block_number()

        with allure.step("验证响应"):
            assert rpc_validator.validate_rpc_response(response), \
                f"RPC 调用失败: {response.status_code}"

            block_number = rpc_validator.extract_rpc_result(response)
            assert block_number, "区块号不能为空"
            assert block_number.startswith("0x"), "区块号格式错误"

            print(f"当前区块号: {block_number}")

    def test_get_block_by_number(self, blockchain_rpc, rpc_validator):
        """示例：根据区块号获取区块信息"""
        # 先获取最新区块号
        response = blockchain_rpc.get_block_number()
        block_number = rpc_validator.extract_rpc_result(response)

        with allure.step(f"获取区块 {block_number} 的详细信息"):
            response = blockchain_rpc.get_block_by_number(block_number, True)

        with allure.step("验证区块信息"):
            assert rpc_validator.validate_rpc_response(response)
            block_info = rpc_validator.extract_rpc_result(response)

            # 验证区块结构
            assert "number" in block_info, "缺少 number 字段"
            assert "hash" in block_info, "缺少 hash 字段"
            assert "transactions" in block_info, "缺少 transactions 字段"

            print(f"区块哈希: {block_info['hash']}")
            print(f"交易数量: {len(block_info['transactions'])}")

    def test_get_transaction_count(self, blockchain_rpc, rpc_validator, test_data):
        """示例：获取地址的交易数量"""
        # 使用测试数据工厂生成地址
        address = test_data.unique_wallet_address()

        with allure.step(f"获取地址 {address} 的交易数量"):
            response = blockchain_rpc.get_transaction_count(address, "latest")

        with allure.step("验证交易数量"):
            assert rpc_validator.validate_rpc_response(response)
            tx_count = rpc_validator.extract_rpc_result(response)

            assert tx_count is not None, "交易数量不能为空"
            print(f"交易数量: {int(tx_count, 16)}")


@allure.feature("RPC 单接口测试")
@allure.story("合约接口")
class TestContractRPCExamples:
    """合约 RPC 单接口测试示例"""

    def test_call_contract(self, contract_rpc, rpc_validator, test_data):
        """示例：调用合约方法"""
        # 构造合约调用参数
        contract_address = test_data.random_contract_address()
        data = "0x70a08231" + "0" * 24 + test_data.unique_wallet_address()[2:]  # balanceOf

        with allure.step("调用合约 balanceOf 方法"):
            response = contract_rpc.call_contract(
                to_address=contract_address,
                data=data,
                block="latest"
            )

        with allure.step("验证调用结果"):
            assert rpc_validator.validate_rpc_response(response)
            result = rpc_validator.extract_rpc_result(response)

            assert result, "合约调用结果不能为空"
            print(f"合约返回值: {result}")

    def test_estimate_gas(self, contract_rpc, rpc_validator, test_data):
        """示例：估算 Gas"""
        from_address = test_data.unique_wallet_address()
        to_address = test_data.unique_wallet_address()

        with allure.step("估算转账 Gas"):
            response = contract_rpc.estimate_gas(
                from_address=from_address,
                to_address=to_address,
                value="0x1"
            )

        with allure.step("验证 Gas 估算"):
            assert rpc_validator.validate_rpc_response(response)
            gas_estimate = rpc_validator.extract_rpc_result(response)

            assert gas_estimate, "Gas 估算不能为空"
            gas_value = int(gas_estimate, 16)
            assert gas_value > 0, "Gas 估算值必须大于 0"

            print(f"估算 Gas: {gas_value}")


# ==================== 场景测试示例 ====================

@allure.feature("RPC 场景测试")
@allure.story("区块链查询场景")
class TestBlockchainScenarios:
    """区块链查询场景测试示例"""

    def test_query_latest_block_scenario(self, latest_block):
        """场景：查询最新区块完整信息"""
        with allure.step("验证场景返回数据"):
            assert "block_number" in latest_block
            assert "block_info" in latest_block

            block_number = latest_block["block_number"]
            block_info = latest_block["block_info"]

            # 验证区块信息完整性
            assert block_info["number"] == block_number
            assert "hash" in block_info
            assert "parentHash" in block_info
            assert "timestamp" in block_info

            print(f"✅ 场景执行成功")
            print(f"区块号: {block_number}")
            print(f"区块哈希: {block_info['hash']}")
            print(f"时间戳: {block_info['timestamp']}")

    def test_block_history_scenario(self, blockchain_rpc, rpc_validator):
        """场景：查询历史区块"""
        with allure.step("获取最新区块号"):
            response = blockchain_rpc.get_block_number()
            latest_block = int(rpc_validator.extract_rpc_result(response), 16)

        with allure.step("查询最近 5 个区块"):
            blocks = []
            for i in range(5):
                block_num = hex(latest_block - i)
                response = blockchain_rpc.get_block_by_number(block_num, False)
                assert rpc_validator.validate_rpc_response(response)
                blocks.append(rpc_validator.extract_rpc_result(response))

        with allure.step("验证区块连续性"):
            for i in range(len(blocks) - 1):
                current_block = blocks[i]
                next_block = blocks[i + 1]
                assert current_block["parentHash"] == next_block["hash"], \
                    "区块链不连续"

            print(f"✅ 验证了 {len(blocks)} 个连续区块")


@allure.feature("RPC 场景测试")
@allure.story("交易场景")
class TestTransactionScenarios:
    """交易场景测试示例"""

    def test_transaction_lifecycle_scenario(self, transaction_with_receipt):
        """场景：交易生命周期（发送 -> 轮询 -> 获取回执）"""
        with allure.step("验证场景返回数据"):
            assert "tx_hash" in transaction_with_receipt
            tx_hash = transaction_with_receipt["tx_hash"]
            receipt = transaction_with_receipt["receipt"]

            print(f"交易哈希: {tx_hash}")

            if receipt:
                print(f"✅ 交易已确认")
                print(f"区块号: {receipt.get('blockNumber')}")
                print(f"Gas 使用: {receipt.get('gasUsed')}")
            else:
                print(f"⏳ 交易仍在等待确认（示例场景）")


# ==================== 数据驱动测试示例 ====================

@allure.feature("RPC 数据驱动测试")
@allure.story("参数化测试")
class TestParameterizedRPC:
    """参数化 RPC 测试示例"""

    @pytest.mark.parametrize("block_param", [
        "latest",
        "earliest",
        "pending"
    ])
    def test_get_block_with_different_params(self, blockchain_rpc, rpc_validator, block_param):
        """示例：使用不同参数获取区块"""
        with allure.step(f"获取 {block_param} 区块"):
            response = blockchain_rpc.get_block_by_number(block_param, False)

        with allure.step("验证响应"):
            assert rpc_validator.validate_rpc_response(response)
            block_info = rpc_validator.extract_rpc_result(response)

            if block_info:  # pending 可能为 null
                assert "number" in block_info or block_param == "pending"
                print(f"✅ {block_param} 区块获取成功")

    @pytest.mark.parametrize("address,expected_format", [
        ("0x0000000000000000000000000000000000000000", "0x"),
        ("0x" + "1" * 40, "0x"),
    ])
    def test_get_balance_with_different_addresses(
        self, blockchain_rpc, rpc_validator, address, expected_format
    ):
        """示例：查询不同地址的余额"""
        with allure.step(f"查询地址 {address} 的余额"):
            response = blockchain_rpc.get_balance(address, "latest")

        with allure.step("验证余额格式"):
            assert rpc_validator.validate_rpc_response(response)
            balance = rpc_validator.extract_rpc_result(response)

            assert balance.startswith(expected_format)
            print(f"地址 {address[:10]}... 余额: {int(balance, 16)} wei")


# ==================== 错误处理示例 ====================

@allure.feature("RPC 错误处理")
@allure.story("异常场景")
class TestRPCErrorHandling:
    """RPC 错误处理示例"""

    def test_invalid_block_number(self, blockchain_rpc, rpc_validator):
        """示例：处理无效区块号"""
        invalid_block = "0xffffffffffffffffff"

        with allure.step("请求无效区块"):
            response = blockchain_rpc.get_block_by_number(invalid_block, False)

        with allure.step("验证错误响应"):
            # 根据节点实现，可能返回 null 或错误
            if rpc_validator.validate_rpc_response(response):
                result = rpc_validator.extract_rpc_result(response)
                assert result is None, "无效区块应返回 null"
            else:
                print("节点返回错误响应（符合预期）")

    def test_invalid_address_format(self, blockchain_rpc):
        """示例：处理无效地址格式"""
        invalid_address = "0xinvalid"

        with allure.step("请求无效地址的余额"):
            response = blockchain_rpc.get_balance(invalid_address, "latest")

        with allure.step("验证错误处理"):
            # 应该返回错误或 400 状态码
            assert response.status_code >= 400 or "error" in response.json()
            print("✅ 正确处理了无效地址")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--allure-results-dir=allure-results"])
