#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : test_blockchain_scenario.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : 
"""
import pytest
import allure
from tests.rpc.fixtures.rpc_fixtures import attach_rpc_request, attach_rpc_response, attach_rpc_step


@allure.feature("区块链 RPC")
@allure.story("区块查询")
class TestBlockchainScenario:
    """区块链 RPC 场景测试"""

    @allure.title("场景：查询最新区块信息")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("查询最新区块号和区块详情")
    def test_query_latest_block(self, latest_block):
        """
        场景：查询最新区块信息
        使用 fixture：latest_block
        """
        block_number = latest_block['block_number']
        block_info = latest_block['block_info']

        attach_rpc_step("区块信息",
                       block_number=block_number,
                       transactions_count=len(block_info.get('transactions', [])) if block_info else 0)

    @allure.title("场景：查询地址余额→交易数")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("查询指定地址的余额和交易数")
    def test_query_address_info(self, blockchain_rpc, test_data, rpc_validator):
        """
        场景：查询地址余额→交易数
        组装：blockchain_rpc
        """
        address = test_data.unique_wallet_address()

        # 步骤1：查询余额
        with allure.step("查询地址余额"):
            response = blockchain_rpc.get_balance(address)
            attach_rpc_request("eth_getBalance", [address, "latest"])
            attach_rpc_response(response)

            assert rpc_validator.validate_rpc_response(response), \
                f"查询余额失败: {response.status_code}"

            balance = rpc_validator.extract_rpc_result(response)
            attach_rpc_step("余额信息", address=address, balance=balance)

        # 步骤2：查询交易数
        with allure.step("查询交易数"):
            response = blockchain_rpc.get_transaction_count(address)
            attach_rpc_request("eth_getTransactionCount", [address, "latest"])
            attach_rpc_response(response)

            assert rpc_validator.validate_rpc_response(response), \
                f"查询交易数失败: {response.status_code}"

            tx_count = rpc_validator.extract_rpc_result(response)
            attach_rpc_step("交易数", address=address, count=tx_count)

    @allure.title("场景：查询gas价格→估算gas")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("查询当前gas价格并估算交易gas")
    def test_query_gas_info(self, blockchain_rpc, test_data, rpc_validator):
        """
        场景：查询gas价格→估算gas
        组装：blockchain_rpc
        """
        # 步骤1：查询gas价格
        with allure.step("查询gas价格"):
            response = blockchain_rpc.get_gas_price()
            attach_rpc_request("eth_gasPrice")
            attach_rpc_response(response)

            assert rpc_validator.validate_rpc_response(response), \
                f"查询gas价格失败: {response.status_code}"

            gas_price = rpc_validator.extract_rpc_result(response)
            attach_rpc_step("Gas价格", gas_price=gas_price)

        # 步骤2：估算gas
        with allure.step("估算交易gas"):
            tx_object = {
                "from": test_data.unique_wallet_address(),
                "to": test_data.unique_wallet_address(),
                "value": "0x1"
            }
            response = blockchain_rpc.estimate_gas(tx_object)
            attach_rpc_request("eth_estimateGas", [tx_object])
            attach_rpc_response(response)

            assert rpc_validator.validate_rpc_response(response), \
                f"估算gas失败: {response.status_code}"

            gas_estimate = rpc_validator.extract_rpc_result(response)
            attach_rpc_step("Gas估算", estimate=gas_estimate)
