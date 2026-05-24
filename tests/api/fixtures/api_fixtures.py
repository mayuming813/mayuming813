#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : api_fixtures.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : 
"""
import pytest
import allure
import json
from tests.api.apis.user_api import UserAPI
from tests.api.apis.wallet_api import WalletAPI
from tests.api.apis.transaction_api import TransactionAPI
from tests.api.apis.contract_api import ContractAPI
from framework.utils.http_client import HTTPClient
from framework.utils.test_data_factory import TestDataFactory
from framework.utils.api_validator import APIValidator
from framework.core.config import config


# ==================== Allure 报告增强辅助函数 ====================

def attach_request_info(method: str, url: str, **kwargs):
    """
    附加请求信息到 Allure 报告
    :param method: 请求方法
    :param url: 请求 URL
    :param kwargs: 其他请求参数（params, json, headers等）
    """
    request_info = {
        'method': method.upper(),
        'url': url,
    }

    if 'params' in kwargs and kwargs['params']:
        request_info['params'] = kwargs['params']

    if 'json' in kwargs and kwargs['json']:
        request_info['body'] = kwargs['json']

    if 'headers' in kwargs and kwargs['headers']:
        request_info['headers'] = kwargs['headers']

    allure.attach(
        json.dumps(request_info, indent=2, ensure_ascii=False),
        name="📤 请求信息",
        attachment_type=allure.attachment_type.JSON
    )


def attach_response_info(response):
    """
    附加响应信息到 Allure 报告
    :param response: Response 对象
    """
    response_info = {
        'status_code': response.status_code,
        'headers': dict(response.headers),
    }

    try:
        response_info['body'] = response.json()
    except:
        response_info['body'] = response.text

    allure.attach(
        json.dumps(response_info, indent=2, ensure_ascii=False),
        name="📥 响应信息",
        attachment_type=allure.attachment_type.JSON
    )


def attach_step_info(step_name: str, **data):
    """
    附加步骤信息到 Allure 报告
    :param step_name: 步骤名称
    :param data: 步骤数据
    """
    allure.attach(
        json.dumps(data, indent=2, ensure_ascii=False),
        name=f"📝 {step_name}",
        attachment_type=allure.attachment_type.JSON
    )




@pytest.fixture(scope="function")
def http_client():
    """HTTP 客户端 fixture"""
    client = HTTPClient(base_url=config.backend_api_url)
    yield client
    client.close()


@pytest.fixture(scope="function")
def user_api(http_client):
    """用户 API fixture"""
    return UserAPI(client=http_client)


@pytest.fixture(scope="function")
def wallet_api(http_client):
    """钱包 API fixture"""
    return WalletAPI(client=http_client)


@pytest.fixture(scope="function")
def transaction_api(http_client):
    """交易 API fixture"""
    return TransactionAPI(client=http_client)


@pytest.fixture(scope="function")
def contract_api(http_client):
    """合约 API fixture"""
    return ContractAPI(client=http_client)


@pytest.fixture(scope="function")
def validator():
    """API 验证器 fixture"""
    return APIValidator()


@pytest.fixture(scope="function")
def test_data():
    """测试数据工厂 fixture"""
    return TestDataFactory()


# ==================== 场景 Fixtures（模块化组装）====================

@pytest.fixture(scope="function")
def created_user(user_api, test_data, validator):
    """
    场景模块：创建一个用户
    返回：用户数据和创建响应
    """
    user_data = test_data.create_user_data()

    with allure.step("创建用户"):
        attach_step_info("用户数据", **user_data)

        # 调用单接口
        response = user_api.create_user(
            username=user_data['username'],
            password=user_data['password'],
            email=user_data['email']
        )

        attach_request_info('POST', '/api/user/create', json=user_data)
        attach_response_info(response)

        # 验证
        assert validator.validate_status_code_in(response, [200, 201]), \
            f"创建用户失败: {response.status_code}"

        # 提取 user_id（如果有）
        user_id = validator.extract_json_field(response, 'data.user_id')

    return {
        'user_data': user_data,
        'response': response,
        'user_id': user_id
    }


@pytest.fixture(scope="function")
def logged_in_user(user_api, created_user, validator):
    """
    场景模块：创建用户并登录
    依赖：created_user
    返回：用户数据、token 和登录响应
    """











    with allure.step("用户登录"):
        login_data = {
            'username': user_data['username'],
            'password': user_data['password']
        }
        attach_step_info("登录数据", **login_data)

        # 调用单接口：登录
        response = user_api.login(
            username=user_data['username'],
            password=user_data['password']
        )

        attach_request_info('POST', '/api/auth/login', json=login_data)
        attach_response_info(response)

        # 验证
        assert validator.validate_status_code(response, 200), \
            f"登录失败: {response.status_code}"

        # 提取 token
        token = validator.extract_json_field(response, 'data.token')
        assert token, "登录响应缺少 token"

        # 设置 token 到客户端
        user_api.client.set_auth_token(token)

    return {
        'user_data': user_data,
        'token': token,
        'response': response,
        'user_id': created_user.get('user_id')
    }


@pytest.fixture(scope="function")
def user_with_info(user_api, logged_in_user, validator):
    """
    场景模块：创建用户、登录并获取用户信息
    依赖：logged_in_user
    返回：用户数据、token 和用户信息
    """
    # 调用单接口：获取用户信息
    response = user_api.get_user_info()

    # 验证
    assert validator.validate_status_code(response, 200), \
        f"获取用户信息失败: {response.status_code}"

    user_info = validator.extract_json_field(response, 'data')

    return {
        **logged_in_user,
        'user_info': user_info,
        'info_response': response
    }


@pytest.fixture(scope="function")
def multiple_users(user_api, test_data, validator):
    """
    场景模块：创建多个用户
    返回：用户列表
    """
    users = []

    for i in range(3):
        user_data = test_data.create_user_data()

        # 调用单接口
        response = user_api.create_user(
            username=user_data['username'],
            password=user_data['password'],
            email=user_data['email']
        )

        # 验证
        assert validator.validate_status_code_in(response, [200, 201]), \
            f"创建用户 #{i+1} 失败"

        user_id = validator.extract_json_field(response, 'data.user_id')

        users.append({
            'user_data': user_data,
            'user_id': user_id,
            'response': response
        })

    return users


# ==================== 数据准备 Fixtures ====================

@pytest.fixture(scope="function")
def unique_user_data(test_data):
    """
    数据准备：生成唯一的用户数据
    用于并发测试，避免数据冲突
    """
    return test_data.create_user_data()


@pytest.fixture(scope="function")
def unique_wallet_address(test_data):
    """
    数据准备：生成唯一的钱包地址
    """
    return test_data.unique_wallet_address()
