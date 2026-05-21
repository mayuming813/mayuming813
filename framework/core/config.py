#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : config.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : 
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv


class Config:
    """配置管理类"""

    _instance = None
    _config: Dict[str, Any] = {}
    _env_loaded = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_env()
            cls._instance._load_config()
        return cls._instance

    def _load_env(self):
        """加载环境变量"""
        if not self._env_loaded:
            # 加载 .env 文件
            env_file = Path(__file__).parent.parent.parent / ".env"
            if env_file.exists():
                load_dotenv(env_file)
            self._env_loaded = True

    def _load_config(self):
        """加载配置文件"""
        config_dir = Path(__file__).parent.parent.parent / "config"

        # 优先加载 local.yaml，不存在则使用 config.example.yaml
        local_config = config_dir / "local.yaml"
        example_config = config_dir / "config.example.yaml"

        if local_config.exists():
            config_file = local_config
        elif example_config.exists():
            config_file = example_config
        else:
            # 如果配置文件都不存在，使用空配置（依赖环境变量）
            self._config = {}
            return

        with open(config_file, 'r', encoding='utf-8') as f:
            self._config = yaml.safe_load(f) or {}

    def get(self, key: str, default=None):
        """
        获取配置项
        优先级：环境变量 > 配置文件
        """
        # 将 key 转换为环境变量格式（例如：ui.base_url -> UI_BASE_URL）
        env_key = key.upper().replace('.', '_')
        env_value = os.getenv(env_key)

        if env_value is not None:
            # 尝试转换类型
            return self._convert_type(env_value)

        # 从配置文件获取
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default

    def _convert_type(self, value: str):
        """转换环境变量类型"""
        # 布尔值
        if value.lower() in ('true', 'yes', '1'):
            return True
        if value.lower() in ('false', 'no', '0'):
            return False

        # 数字
        try:
            if '.' in value:
                return float(value)
            return int(value)
        except ValueError:
            pass

        return value

    @property
    def active_network(self) -> str:
        """当前激活的网络"""
        return os.getenv('ACTIVE_NETWORK', 'local')

    @property
    def rpc_url(self) -> str:
        """当前网络的 RPC URL"""
        network = self.active_network
        env_key = f"{network.upper()}_RPC_URL"
        return os.getenv(env_key, 'http://127.0.0.1:8545')

    @property
    def chain_id(self) -> int:
        """当前网络的 Chain ID"""
        network = self.active_network
        env_key = f"{network.upper()}_CHAIN_ID"
        return int(os.getenv(env_key, '1337'))

    def get_contract(self, name: str) -> Dict[str, str]:
        """获取合约配置"""
        contract_name = name.upper()
        return {
            'address': os.getenv(f'{contract_name}_CONTRACT_ADDRESS', ''),
            'abi_path': os.getenv(f'{contract_name}_ABI_PATH', f'artifacts/{name.capitalize()}.json')
        }

    def get_account(self, name: str) -> Dict[str, str]:
        """获取账户配置"""
        account_name = name.upper()
        return {
            'address': os.getenv(f'{account_name}_ADDRESS', ''),
            'private_key': os.getenv(f'{account_name}_PRIVATE_KEY', '')
        }

    @property
    def backend_api_url(self) -> str:
        """后端 API URL"""
        return os.getenv('BACKEND_API_URL', 'http://localhost:3000')

    @property
    def api_timeout(self) -> int:
        """API 超时时间"""
        return int(os.getenv('API_TIMEOUT', '30'))

    @property
    def dapp_base_url(self) -> str:
        """DApp 基础 URL"""
        return os.getenv('DAPP_BASE_URL', 'http://localhost:3001')

    @property
    def metamask_seed_phrase(self) -> str:
        """MetaMask 助记词"""
        return os.getenv('METAMASK_SEED_PHRASE', '')

    @property
    def metamask_password(self) -> str:
        """MetaMask 密码"""
        return os.getenv('METAMASK_PASSWORD', '')

    @property
    def log_level(self) -> str:
        """日志级别"""
        return os.getenv('LOG_LEVEL', self.get('logging.level', 'INFO'))


# 全局配置实例
config = Config()
