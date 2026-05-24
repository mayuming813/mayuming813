#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : test_data_factory_examples.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : 
"""
import pytest
import allure
from framework.utils.test_data_factory import TestDataFactory


@allure.feature("测试数据工厂")
@allure.story("基础数据生成")
class TestBasicDataGeneration:
    """基础数据生成示例"""

    def test_unique_identifiers(self):
        """示例：生成唯一标识符"""
        factory = TestDataFactory()

        # 生成唯一 ID
        unique_id = factory.unique_id()
        print(f"唯一ID: {unique_id}")

        # 生成短 ID
        short_id = factory.short_id(length=8)
        print(f"短ID: {short_id}")

        # 生成时间戳
        timestamp = factory.timestamp()
        print(f"时间戳（毫秒）: {timestamp}")

        timestamp_sec = factory.timestamp_seconds()
        print(f"时间戳（秒）: {timestamp_sec}")

    def test_random_strings_and_numbers(self):
        """示例：生成随机字符串和数字"""
        factory = TestDataFactory()

        # 生成随机字符串
        random_str = factory.random_string(length=10)
        print(f"随机字符串: {random_str}")

        # 生成随机数字
        random_num = factory.random_number(min_val=1, max_val=100)
        print(f"随机数字: {random_num}")

        # 生成随机浮点数
        random_float = factory.random_float(min_val=0.0, max_val=100.0, decimals=2)
        print(f"随机浮点数: {random_float}")

        # 生成随机布尔值
        random_bool = factory.random_bool()
        print(f"随机布尔值: {random_bool}")


@allure.feature("测试数据工厂")
@allure.story("用户数据生成")
class TestUserDataGeneration:
    """用户数据生成示例"""

    def test_user_credentials(self):
        """示例：生成用户凭证"""
        factory = TestDataFactory()

        # 生成唯一用户名
        username = factory.unique_username(prefix="test_user")
        print(f"用户名: {username}")

        # 生成唯一邮箱
        email = factory.unique_email(domain="example.com")
        print(f"邮箱: {email}")

        # 生成随机密码
        password = factory.random_password(length=12, special_chars=True)
        print(f"密码: {password}")

    def test_user_profile(self):
        """示例：生成用户资料"""
        factory = TestDataFactory()

        # 生成随机姓名
        name = factory.random_name()
        print(f"姓名: {name}")

        # 生成随机手机号
        phone = factory.random_phone()
        print(f"手机号: {phone}")

        # 生成随机地址
        address = factory.random_address()
        print(f"地址: {address}")

        # 生成随机公司名
        company = factory.random_company()
        print(f"公司: {company}")

    def test_complete_user_data(self):
        """示例：生成完整用户数据"""
        # 使用默认值
        user_data = TestDataFactory.create_user_data()
        print(f"用户数据: {user_data}")

        # 自定义部分字段
        custom_user = TestDataFactory.create_user_data(
            username="custom_user",
            email="custom@example.com"
        )
        print(f"自定义用户: {custom_user}")


@allure.feature("测试数据工厂")
@allure.story("Web3 数据生成")
class TestWeb3DataGeneration:
    """Web3 数据生成示例"""

    def test_wallet_addresses(self):
        """示例：生成钱包地址"""
        factory = TestDataFactory()

        # 生成钱包地址
        wallet_address = factory.unique_wallet_address()
        print(f"钱包地址: {wallet_address}")

        # 生成合约地址
        contract_address = factory.random_contract_address()
        print(f"合约地址: {contract_address}")

        # 生成私钥（仅测试用）
        private_key = factory.random_private_key()
        print(f"私钥: {private_key}")

    def test_transaction_data(self):
        """示例：生成交易数据"""
        factory = TestDataFactory()

        # 生成交易哈希
        tx_hash = factory.random_tx_hash()
        print(f"交易哈希: {tx_hash}")

        # 生成代币数量
        token_amount = factory.random_token_amount(decimals=18, min_val=0.1, max_val=1000.0)
        print(f"代币数量（wei）: {token_amount}")

        # 生成完整交易数据
        tx_data = TestDataFactory.create_transaction_data()
        print(f"交易数据: {tx_data}")

        # 自定义交易数据
        custom_tx = TestDataFactory.create_transaction_data(
            from_address="0x1234567890123456789012345678901234567890",
            value=1000000000000000000  # 1 ETH
        )
        print(f"自定义交易: {custom_tx}")


@allure.feature("测试数据工厂")
@allure.story("列表和批量数据")
class TestListDataGeneration:
    """列表和批量数据生成示例"""

    def test_random_selection(self):
        """示例：随机选择"""
        factory = TestDataFactory()

        choices = ['pending', 'processing', 'completed', 'failed']

        # 随机选择一个
        choice = factory.random_choice(choices)
        print(f"随机选择: {choice}")

        # 随机选择多个（可重复）
        multiple_choices = factory.random_choices(choices, count=3)
        print(f"随机选择（可重复）: {multiple_choices}")

        # 随机抽样（不重复）
        sample = factory.random_sample(choices, count=2)
        print(f"随机抽样（不重复）: {sample}")

    def test_batch_generation(self):
        """示例：批量生成数据"""
        factory = TestDataFactory()

        # 批量生成用户
        users = [TestDataFactory.create_user_data() for _ in range(3)]
        print(f"批量用户: {len(users)} 个")

        # 批量生成订单
        orders = [TestDataFactory.create_order_data() for _ in range(5)]
        print(f"批量订单: {len(orders)} 个")


@allure.feature("测试数据工厂")
@allure.story("参数化测试数据")
class TestParameterizedData:
    """参数化测试数据示例"""

    def test_test_matrix(self):
        """示例：创建测试矩阵"""
        # 定义参数
        params = {
            'amount': [0, 1, 100],
            'status': ['active', 'inactive'],
            'type': ['A', 'B']
        }

        # 生成测试矩阵（笛卡尔积）
        test_cases = TestDataFactory.create_test_matrix(params)
        print(f"测试用例数量: {len(test_cases)}")
        for i, case in enumerate(test_cases):
            print(f"用例 {i+1}: {case}")

    def test_boundary_values(self):
        """示例：创建边界值"""
        # 生成边界值
        boundary_values = TestDataFactory.create_boundary_values(min_val=1, max_val=100)
        print(f"边界值: {boundary_values}")

        # 用于参数化测试
        for value in boundary_values:
            print(f"测试值: {value}")


@allure.feature("测试数据工厂")
@allure.story("复杂数据结构")
class TestComplexDataStructures:
    """复杂数据结构示例"""

    def test_order_data(self):
        """示例：生成订单数据"""
        # 生成默认订单
        order = TestDataFactory.create_order_data()
        print(f"订单数据: {order}")

        # 自定义订单
        custom_order = TestDataFactory.create_order_data(
            product_id=12345,
            quantity=5,
            price=99.99,
            status='paid'
        )
        print(f"自定义订单: {custom_order}")

    def test_nested_data(self):
        """示例：生成嵌套数据结构"""
        factory = TestDataFactory()

        # 生成用户及其订单
        user = TestDataFactory.create_user_data()
        user['orders'] = [
            TestDataFactory.create_order_data() for _ in range(3)
        ]
        print(f"用户及订单: {user}")


@allure.feature("测试数据工厂")
@allure.story("数据持久化")
class TestDataPersistence:
    """数据持久化示例"""

    def test_save_and_load_json(self, tmp_path):
        """示例：保存和加载 JSON 数据"""
        factory = TestDataFactory()

        # 生成测试数据
        test_data = {
            'users': [TestDataFactory.create_user_data() for _ in range(3)],
            'orders': [TestDataFactory.create_order_data() for _ in range(5)]
        }

        # 保存到文件
        file_path = tmp_path / "test_data.json"
        factory.save_to_json(test_data, str(file_path))
        print(f"数据已保存到: {file_path}")

        # 从文件加载
        loaded_data = factory.load_from_json(str(file_path))
        print(f"加载的数据: {len(loaded_data['users'])} 个用户, {len(loaded_data['orders'])} 个订单")

        assert len(loaded_data['users']) == 3
        assert len(loaded_data['orders']) == 5


# ==================== 实际使用示例 ====================

def example_api_test():
    """示例：在 API 测试中使用"""
    factory = TestDataFactory()

    # 创建测试用户
    user_data = factory.create_user_data()

    # 模拟 API 调用
    # response = api.create_user(**user_data)
    # assert response.status_code == 201

    print(f"API 测试用户: {user_data}")


def example_ui_test():
    """示例：在 UI 测试中使用"""
    factory = TestDataFactory()

    # 生成表单数据
    username = factory.unique_username()
    email = factory.unique_email()
    password = factory.random_password()

    # 模拟 UI 操作
    # page.fill("#username", username)
    # page.fill("#email", email)
    # page.fill("#password", password)

    print(f"UI 测试数据: {username}, {email}")


def example_contract_test():
    """示例：在合约测试中使用"""
    factory = TestDataFactory()

    # 生成测试地址
    from_address = factory.unique_wallet_address()
    to_address = factory.unique_wallet_address()
    amount = factory.random_token_amount(decimals=18, min_val=1.0, max_val=100.0)

    # 模拟合约调用
    # tx = contract.transfer(from_address, to_address, amount)

    print(f"合约测试数据: {from_address} -> {to_address}, amount: {amount}")


if __name__ == "__main__":
    # 运行示例
    print("=" * 50)
    print("测试数据工厂使用示例")
    print("=" * 50)

    example_api_test()
    example_ui_test()
    example_contract_test()
