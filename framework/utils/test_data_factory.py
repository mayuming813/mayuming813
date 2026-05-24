#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : test_data_factory.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : 
"""
import uuid
import time
import random
import string
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
from faker import Faker


class TestDataFactory:
    """测试数据工厂 - 提供常用测试数据构造能力"""

    def __init__(self, locale='zh_CN'):
        """
        初始化
        :param locale: 语言环境，默认中文
        """
        self.faker = Faker(locale)

    # ==================== 基础数据生成 ====================

    @staticmethod
    def unique_id() -> str:
        """生成唯一 ID"""
        return str(uuid.uuid4())

    @staticmethod
    def short_id(length: int = 8) -> str:
        """
        生成短 ID
        :param length: ID 长度
        :return: 短 ID
        """
        return uuid.uuid4().hex[:length]

    @staticmethod
    def timestamp() -> int:
        """生成时间戳（毫秒）"""
        return int(time.time() * 1000)

    @staticmethod
    def timestamp_seconds() -> int:
        """生成时间戳（秒）"""
        return int(time.time())

    @staticmethod
    def random_string(length: int = 10, chars: str = None) -> str:
        """
        生成随机字符串
        :param length: 字符串长度
        :param chars: 字符集，默认字母+数字
        :return: 随机字符串
        """
        if chars is None:
            chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))

    @staticmethod
    def random_number(min_val: int = 1, max_val: int = 100) -> int:
        """
        生成随机数字
        :param min_val: 最小值
        :param max_val: 最大值
        :return: 随机数字
        """
        return random.randint(min_val, max_val)

    @staticmethod
    def random_float(min_val: float = 0.0, max_val: float = 100.0, decimals: int = 2) -> float:
        """
        生成随机浮点数
        :param min_val: 最小值
        :param max_val: 最大值
        :param decimals: 小数位数
        :return: 随机浮点数
        """
        return round(random.uniform(min_val, max_val), decimals)

    @staticmethod
    def random_bool() -> bool:
        """生成随机布尔值"""
        return random.choice([True, False])

    # ==================== 用户相关数据 ====================

    @staticmethod
    def unique_username(prefix: str = "test_user") -> str:
        """
        生成唯一用户名
        :param prefix: 前缀
        :return: 唯一用户名
        """
        timestamp = int(time.time() * 1000)
        return f"{prefix}_{timestamp}_{uuid.uuid4().hex[:8]}"

    @staticmethod
    def unique_email(domain: str = "test.com") -> str:
        """
        生成唯一邮箱
        :param domain: 域名
        :return: 唯一邮箱
        """
        timestamp = int(time.time() * 1000)
        unique_id = uuid.uuid4().hex[:8]
        return f"test_{timestamp}_{unique_id}@{domain}"

    def random_password(self, length: int = 12, special_chars: bool = True) -> str:
        """
        生成随机密码
        :param length: 密码长度
        :param special_chars: 是否包含特殊字符
        :return: 随机密码
        """
        return self.faker.password(
            length=length,
            special_chars=special_chars,
            digits=True,
            upper_case=True,
            lower_case=True
        )

    def random_phone(self) -> str:
        """生成随机手机号"""
        return self.faker.phone_number()

    def random_address(self) -> str:
        """生成随机地址"""
        return self.faker.address()

    def random_name(self) -> str:
        """生成随机姓名"""
        return self.faker.name()

    def random_company(self) -> str:
        """生成随机公司名"""
        return self.faker.company()

    # ==================== Web3 相关数据 ====================

    @staticmethod
    def unique_wallet_address() -> str:
        """
        生成唯一的钱包地址（模拟）
        :return: 钱包地址（0x + 40位十六进制）
        """
        return f"0x{uuid.uuid4().hex[:40]}"

    @staticmethod
    def random_private_key() -> str:
        """
        生成随机私钥（模拟，仅用于测试）
        :return: 私钥（0x + 64位十六进制）
        """
        return f"0x{uuid.uuid4().hex}{uuid.uuid4().hex}"

    @staticmethod
    def random_tx_hash() -> str:
        """
        生成随机交易哈希（模拟）
        :return: 交易哈希（0x + 64位十六进制）
        """
        return f"0x{uuid.uuid4().hex}{uuid.uuid4().hex}"

    @staticmethod
    def random_contract_address() -> str:
        """
        生成随机合约地址（模拟）
        :return: 合约地址
        """
        return TestDataFactory.unique_wallet_address()

    @staticmethod
    def random_token_amount(decimals: int = 18, min_val: float = 0.1, max_val: float = 1000.0) -> int:
        """
        生成随机代币数量（wei）
        :param decimals: 代币精度
        :param min_val: 最小值（代币单位）
        :param max_val: 最大值（代币单位）
        :return: 代币数量（wei）
        """
        amount = random.uniform(min_val, max_val)
        return int(amount * (10 ** decimals))

    # ==================== 日期时间相关 ====================

    def random_date(self, start_date: str = None, end_date: str = None) -> str:
        """
        生成随机日期
        :param start_date: 开始日期（格式：YYYY-MM-DD）
        :param end_date: 结束日期（格式：YYYY-MM-DD）
        :return: 随机日期
        """
        if start_date and end_date:
            return self.faker.date_between(start_date=start_date, end_date=end_date).strftime('%Y-%m-%d')
        return self.faker.date()

    def random_datetime(self, days_ago: int = 30) -> str:
        """
        生成随机日期时间
        :param days_ago: 多少天前
        :return: 随机日期时间
        """
        start_date = datetime.now() - timedelta(days=days_ago)
        return self.faker.date_time_between(start_date=start_date).strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def future_timestamp(seconds: int = 3600) -> int:
        """
        生成未来时间戳
        :param seconds: 多少秒后
        :return: 时间戳（秒）
        """
        return int(time.time()) + seconds

    # ==================== 列表和批量数据 ====================

    def random_list(self, generator_func, count: int = 5, **kwargs) -> List[Any]:
        """
        生成随机列表
        :param generator_func: 生成器函数
        :param count: 数量
        :param kwargs: 传递给生成器的参数
        :return: 随机列表
        """
        return [generator_func(**kwargs) for _ in range(count)]

    def random_choice(self, choices: List[Any]) -> Any:
        """
        从列表中随机选择
        :param choices: 选项列表
        :return: 随机选项
        """
        return random.choice(choices)

    def random_choices(self, choices: List[Any], count: int = 3) -> List[Any]:
        """
        从列表中随机选择多个（可重复）
        :param choices: 选项列表
        :param count: 选择数量
        :return: 随机选项列表
        """
        return random.choices(choices, k=count)

    def random_sample(self, choices: List[Any], count: int = 3) -> List[Any]:
        """
        从列表中随机抽样（不重复）
        :param choices: 选项列表
        :param count: 抽样数量
        :return: 随机样本列表
        """
        return random.sample(choices, min(count, len(choices)))

    # ==================== 复杂数据结构 ====================

    @staticmethod
    def create_user_data(**kwargs) -> dict:
        """
        创建用户数据
        :param kwargs: 自定义字段
        :return: 用户数据字典
        """
        factory = TestDataFactory()
        default_data = {
            'username': factory.unique_username(),
            'password': factory.random_password(),
            'email': factory.unique_email(),
            'phone': factory.random_phone(),
            'address': factory.random_address(),
            'wallet_address': factory.unique_wallet_address()
        }
        default_data.update(kwargs)
        return default_data

    @staticmethod
    def create_order_data(**kwargs) -> dict:
        """
        创建订单数据
        :param kwargs: 自定义字段
        :return: 订单数据字典
        """
        factory = TestDataFactory()
        default_data = {
            'order_id': factory.unique_id(),
            'product_id': factory.random_number(1, 1000),
            'quantity': factory.random_number(1, 10),
            'price': factory.random_float(10.0, 1000.0),
            'total': 0.0,  # 计算后填充
            'status': factory.random_choice(['pending', 'paid', 'shipped', 'completed']),
            'timestamp': factory.timestamp()
        }
        default_data['total'] = default_data['price'] * default_data['quantity']
        default_data.update(kwargs)
        return default_data

    @staticmethod
    def create_transaction_data(**kwargs) -> dict:
        """
        创建交易数据
        :param kwargs: 自定义字段
        :return: 交易数据字典
        """
        factory = TestDataFactory()
        default_data = {
            'tx_hash': factory.random_tx_hash(),
            'from_address': factory.unique_wallet_address(),
            'to_address': factory.unique_wallet_address(),
            'value': factory.random_token_amount(),
            'gas': factory.random_number(21000, 100000),
            'gas_price': factory.random_number(1000000000, 50000000000),
            'nonce': factory.random_number(0, 100),
            'timestamp': factory.timestamp_seconds()
        }
        default_data.update(kwargs)
        return default_data

    # ==================== 参数化测试数据 ====================

    @staticmethod
    def create_test_matrix(params: Dict[str, List[Any]]) -> List[Dict[str, Any]]:
        """
        创建测试矩阵（笛卡尔积）
        :param params: 参数字典，key为参数名，value为参数值列表
        :return: 测试用例列表
        示例：
            params = {
                'amount': [0, 1, 100],
                'status': ['active', 'inactive']
            }
            结果：[
                {'amount': 0, 'status': 'active'},
                {'amount': 0, 'status': 'inactive'},
                {'amount': 1, 'status': 'active'},
                ...
            ]
        """
        import itertools
        keys = params.keys()
        values = params.values()
        combinations = list(itertools.product(*values))
        return [dict(zip(keys, combo)) for combo in combinations]

    @staticmethod
    def create_boundary_values(min_val: int, max_val: int) -> List[int]:
        """
        创建边界值测试数据
        :param min_val: 最小值
        :param max_val: 最大值
        :return: 边界值列表
        """
        boundary_values = [
            min_val - 1,  # 小于最小值
            min_val,      # 最小值
            min_val + 1,  # 最小值+1
            (min_val + max_val) // 2,  # 中间值
            max_val - 1,  # 最大值-1
            max_val,      # 最大值
            max_val + 1   # 大于最大值
        ]
        return boundary_values

    # ==================== 文件和JSON ====================

    @staticmethod
    def save_to_json(data: Any, file_path: str):
        """
        保存数据到 JSON 文件
        :param data: 数据
        :param file_path: 文件路径
        """
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @staticmethod
    def load_from_json(file_path: str) -> Any:
        """
        从 JSON 文件加载数据
        :param file_path: 文件路径
        :return: 数据
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)


# 全局工厂实例
test_data_factory = TestDataFactory()
