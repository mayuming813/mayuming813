#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : test_data_driven.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : 
"""
import pytest
import allure
from framework.utils.data_loader import DataLoader, parametrize_data, load_data


# ==================== 方式1：使用装饰器（推荐）====================

@allure.feature("数据驱动示例")
@allure.story("用户登录")
@parametrize_data("api/users.yaml", key="valid_users")
def test_valid_login(test_data):
    """测试有效用户登录 - 使用装饰器"""
    username = test_data['username']
    password = test_data['password']
    expected_status = test_data['expected_status']

    # 执行登录逻辑
    # response = login(username, password)
    # assert response.status_code == expected_status

    print(f"测试用户: {username}, 预期状态: {expected_status}")


@allure.feature("数据驱动示例")
@allure.story("用户登录")
@parametrize_data("api/users.yaml", key="invalid_users", ids="expected_error")
def test_invalid_login(test_data):
    """测试无效用户登录 - 使用自定义 ID"""
    username = test_data['username']
    password = test_data['password']
    expected_error = test_data['expected_error']

    # 执行登录逻辑
    # response = login(username, password)
    # assert expected_error in response.json()['error']

    print(f"测试用户: {username}, 预期错误: {expected_error}")


# ==================== 方式2：使用 lambda 自定义 ID ====================

@allure.feature("数据驱动示例")
@allure.story("代币转账")
@parametrize_data("unit/token_transfer.json", ids=lambda x: x['description'])
def test_token_transfer(test_data):
    """测试代币转账 - 使用 lambda 自定义 ID"""
    from_user = test_data['from']
    to_user = test_data['to']
    amount = test_data['amount']
    expected_success = test_data['expected_success']

    print(f"从 {from_user} 转账 {amount} 到 {to_user}, 预期成功: {expected_success}")

    if expected_success:
        # 执行转账并验证成功
        pass
    else:
        # 验证失败并检查错误信息
        expected_error = test_data.get('expected_error')
        print(f"预期错误: {expected_error}")


# ==================== 方式3：CSV 数据驱动 ====================

@allure.feature("数据驱动示例")
@allure.story("UI 转账")
@parametrize_data("ui/transfer_cases.csv", ids="description")
def test_ui_transfer(test_data):
    """测试 UI 转账 - 使用 CSV 数据"""
    recipient = test_data['recipient_address']
    amount = test_data['amount']
    expected_result = test_data['expected_result']
    description = test_data['description']

    print(f"{description}: 转账 {amount} 到 {recipient}, 预期结果: {expected_result}")


# ==================== 方式4：在测试中直接加载数据 ====================

@allure.feature("数据驱动示例")
@allure.story("批量测试")
def test_batch_users():
    """批量测试用户 - 直接加载数据"""
    # 加载所有用户
    all_users = load_data("api/users.yaml", key="users")

    for user in all_users:
        print(f"测试用户: {user['name']}, 邮箱: {user['email']}, 角色: {user['role']}")
        # 执行测试逻辑


# ==================== 方式5：使用 DataLoader 类 ====================

@allure.feature("数据驱动示例")
@allure.story("NFT 购买")
@pytest.mark.parametrize("test_case", DataLoader.get_test_data("integration/nft_purchase.json"))
def test_nft_purchase(test_case):
    """测试 NFT 购买 - 使用 DataLoader 类"""
    description = test_case['description']
    token_amount = test_case['token_amount']
    nft_id = test_case['nft_id']

    print(f"{description}: 使用 {token_amount} 代币购买 NFT#{nft_id}")


# ==================== 方式6：条件过滤数据 ====================

@allure.feature("数据驱动示例")
@allure.story("管理员用户")
def test_admin_users():
    """测试管理员用户 - 过滤数据"""
    all_users = load_data("api/users.yaml", key="users")

    # 过滤出管理员用户
    admin_users = [user for user in all_users if user['role'] == 'admin']

    for user in admin_users:
        print(f"测试管理员: {user['name']}")
        # 执行管理员相关测试


# ==================== 方式7：组合多个数据源 ====================

@allure.feature("数据驱动示例")
@allure.story("组合测试")
def test_combined_data():
    """组合多个数据源"""
    users = load_data("api/users.yaml", key="users")
    transfers = load_data("unit/token_transfer.json")

    print(f"用户数量: {len(users)}")
    print(f"转账案例数量: {len(transfers)}")

    # 可以组合使用这些数据
    for user in users[:2]:  # 取前2个用户
        for transfer in transfers[:2]:  # 取前2个转账案例
            print(f"用户 {user['name']} 执行转账: {transfer['description']}")