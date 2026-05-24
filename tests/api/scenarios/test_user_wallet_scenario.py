#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : test_user_wallet_scenario.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : 
"""
import pytest
import allure
from tests.api.fixtures.api_fixtures import attach_request_info, attach_response_info, attach_step_info


@allure.feature("用户钱包场景")
@allure.story("用户注册并创建钱包")
class TestUserWalletScenario:
    """用户注册并创建钱包场景"""

    @allure.title("场景：用户注册→登录→创建钱包→查询余额")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("完整的用户注册、登录、创建钱包、查询余额流程")
    def test_user_register_and_create_wallet(
        self, user_api, wallet_api, logged_in_user, validator
    ):
        """
        场景：用户注册→登录→创建钱包→查询余额
        组装：logged_in_user + wallet_api
        """
        user_id = logged_in_user.get('user_id')
        user_data = logged_in_user['user_data']

        # 步骤1：创建钱包
        with allure.step("创建ETH钱包"):
            wallet_data = {
                'user_id': user_id,
                'wallet_type': 'ETH'
            }
            attach_step_info("钱包数据", **wallet_data)

            response = wallet_api.create_wallet(
                user_id=user_id,
                wallet_type='ETH'
            )

            attach_request_info('POST', '/api/wallet/create', json=wallet_data)
            attach_response_info(response)

            assert validator.validate_status_code_in(response, [200, 201]), \
                f"创建钱包失败: {response.status_code}"

            wallet_id = validator.extract_json_field(response, 'data.wallet_id')
            wallet_address = validator.extract_json_field(response, 'data.address')

            assert wallet_id, "钱包ID为空"
            assert wallet_address, "钱包地址为空"

        # 步骤2：查询钱包信息
        with allure.step("查询钱包信息"):
            response = wallet_api.get_wallet_info(wallet_id=wallet_id)

            attach_request_info('GET', f'/api/wallet/{wallet_id}')
            attach_response_info(response)

            assert validator.validate_status_code(response, 200), \
                f"查询钱包信息失败: {response.status_code}"

            wallet_info = validator.extract_json_field(response, 'data')
            assert wallet_info.get('wallet_id') == wallet_id, "钱包ID不匹配"

        # 步骤3：查询余额
        with allure.step("查询钱包余额"):
            response = wallet_api.get_balance(address=wallet_address)

            attach_request_info('GET', '/api/wallet/balance', params={'address': wallet_address})
            attach_response_info(response)

            assert validator.validate_status_code(response, 200), \
                f"查询余额失败: {response.status_code}"

            balance = validator.extract_json_field(response, 'data.balance')
            attach_step_info("余额信息", balance=balance, address=wallet_address)

    @allure.title("场景：用户创建多个钱包")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("用户创建多个不同类型的钱包")
    def test_user_create_multiple_wallets(
        self, wallet_api, logged_in_user, validator
    ):
        """
        场景：用户创建多个钱包
        组装：logged_in_user + wallet_api
        """
        user_id = logged_in_user.get('user_id')
        wallet_types = ['ETH', 'BTC', 'USDT']
        created_wallets = []

        for wallet_type in wallet_types:
            with allure.step(f"创建{wallet_type}钱包"):
                wallet_data = {
                    'user_id': user_id,
                    'wallet_type': wallet_type
                }
                attach_step_info(f"{wallet_type}钱包数据", **wallet_data)

                response = wallet_api.create_wallet(
                    user_id=user_id,
                    wallet_type=wallet_type
                )

                attach_request_info('POST', '/api/wallet/create', json=wallet_data)
                attach_response_info(response)

                assert validator.validate_status_code_in(response, [200, 201]), \
                    f"创建{wallet_type}钱包失败: {response.status_code}"

                wallet_id = validator.extract_json_field(response, 'data.wallet_id')
                created_wallets.append({
                    'wallet_id': wallet_id,
                    'wallet_type': wallet_type
                })

        # 验证：查询用户钱包列表
        with allure.step("查询用户钱包列表"):
            response = wallet_api.get_wallet_list(user_id=user_id)

            attach_request_info('GET', '/api/wallet/list', params={'user_id': user_id})
            attach_response_info(response)

            assert validator.validate_status_code(response, 200), \
                f"查询钱包列表失败: {response.status_code}"

            wallet_list = validator.extract_json_field(response, 'data.wallets')
            assert len(wallet_list) >= len(wallet_types), \
                f"钱包数量不匹配，期望至少{len(wallet_types)}个，实际{len(wallet_list)}个"

            attach_step_info("钱包列表", wallets=created_wallets)


@allure.feature("用户钱包场景")
@allure.story("钱包管理")
class TestWalletManagement:
    """钱包管理场景"""

    @allure.title("场景：创建钱包→查询信息→删除钱包")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("完整的钱包生命周期管理")
    def test_wallet_lifecycle(
        self, wallet_api, logged_in_user, validator
    ):
        """
        场景：钱包生命周期管理
        组装：logged_in_user + wallet_api
        """
        user_id = logged_in_user.get('user_id')

        # 步骤1：创建钱包
        with allure.step("创建钱包"):
            response = wallet_api.create_wallet(
                user_id=user_id,
                wallet_type='ETH'
            )

            attach_response_info(response)

            assert validator.validate_status_code_in(response, [200, 201]), \
                f"创建钱包失败: {response.status_code}"

            wallet_id = validator.extract_json_field(response, 'data.wallet_id')

        # 步骤2：查询钱包信息
        with allure.step("查询钱包信息"):
            response = wallet_api.get_wallet_info(wallet_id=wallet_id)

            attach_response_info(response)

            assert validator.validate_status_code(response, 200), \
                f"查询钱包信息失败: {response.status_code}"

        # 步骤3：删除钱包
        with allure.step("删除钱包"):
            response = wallet_api.delete_wallet(wallet_id=wallet_id)

            attach_request_info('DELETE', f'/api/wallet/{wallet_id}')
            attach_response_info(response)

            assert validator.validate_status_code(response, 200), \
                f"删除钱包失败: {response.status_code}"

        # 步骤4：验证钱包已删除
        with allure.step("验证钱包已删除"):
            response = wallet_api.get_wallet_info(wallet_id=wallet_id)

            attach_response_info(response)

            assert validator.validate_status_code(response, 404), \
                f"钱包应该已被删除，但状态码为: {response.status_code}"
