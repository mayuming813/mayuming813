#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : data_loader.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : 
"""
import json
import yaml
import csv
from pathlib import Path
from typing import List, Dict, Any, Union
import pytest


class DataLoader:
    """测试数据加载器"""

    @staticmethod
    def _get_data_path(file_path: str) -> Path:
        """获取数据文件的完整路径"""
        if Path(file_path).is_absolute():
            return Path(file_path)
        return Path(__file__).parent.parent.parent / "data" / file_path

    @staticmethod
    def load_json(file_path: str) -> Any:
        """加载 JSON 文件"""
        path = DataLoader._get_data_path(file_path)
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    @staticmethod
    def load_yaml(file_path: str) -> Any:
        """加载 YAML 文件"""
        path = DataLoader._get_data_path(file_path)
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    @staticmethod
    def load_csv(file_path: str) -> List[Dict[str, str]]:
        """加载 CSV 文件"""
        path = DataLoader._get_data_path(file_path)
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)

    @staticmethod
    def get_test_data(file_name: str, key: str = None):
        """
        根据文件扩展名自动选择加载方式
        如果指定 key，则返回对应的值
        """
        if file_name.endswith('.json'):
            data = DataLoader.load_json(file_name)
        elif file_name.endswith('.yaml') or file_name.endswith('.yml'):
            data = DataLoader.load_yaml(file_name)
        elif file_name.endswith('.csv'):
            data = DataLoader.load_csv(file_name)
        else:
            raise ValueError(f"不支持的文件格式: {file_name}")

        if key and isinstance(data, dict):
            return data.get(key)
        return data

    @staticmethod
    def parametrize(file_path: str, key: str = None, ids: Union[str, callable] = None):
        """
        快捷参数化装饰器

        用法：
        @DataLoader.parametrize("api/users.json")
        def test_users(test_data):
            pass

        @DataLoader.parametrize("api/users.json", key="valid_users")
        def test_valid_users(test_data):
            pass

        @DataLoader.parametrize("api/users.json", ids=lambda x: x['name'])
        def test_users_with_name(test_data):
            pass
        """
        data = DataLoader.get_test_data(file_path, key)

        # 如果不是列表，转换为列表
        if not isinstance(data, list):
            data = [data]

        # 生成测试 ID
        if ids is None:
            # 默认使用索引或 description 字段
            test_ids = [
                item.get('description', item.get('name', f"case_{i}"))
                if isinstance(item, dict) else f"case_{i}"
                for i, item in enumerate(data)
            ]
        elif callable(ids):
            test_ids = [ids(item) for item in data]
        elif isinstance(ids, str):
            test_ids = [item.get(ids, f"case_{i}") for i, item in enumerate(data)]
        else:
            test_ids = None

        return pytest.mark.parametrize("test_data", data, ids=test_ids)


# 便捷函数
def load_data(file_path: str, key: str = None):
    """快捷加载数据函数"""
    return DataLoader.get_test_data(file_path, key)


def parametrize_data(file_path: str, key: str = None, ids: Union[str, callable] = None):
    """快捷参数化装饰器"""
    return DataLoader.parametrize(file_path, key, ids)