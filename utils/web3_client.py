"""
Web3 客户端：连接链、获取测试账户。
"""
from typing import Optional

from eth_account import Account
from web3 import Web3

from config import settings

# 可选：启用未审计的 HD 钱包功能（若需要从助记词派生）
# Account.enable_unaudited_hdwallet_features()

_w3: Optional[Web3] = None


def get_w3() -> Web3:
    """获取单例 Web3 实例。"""
    global _w3
    if _w3 is None:
        _w3 = Web3(Web3.HTTPProvider(settings.eth_rpc_url))
    return _w3


def get_account():
    """
    获取测试用 Account 对象（需在 .env 中配置 TEST_PRIVATE_KEY）。
    @return eth_account.Account
    """
    key = settings.test_private_key
    if not key:
        raise ValueError("TEST_PRIVATE_KEY not set in environment")
    if not key.startswith("0x"):
        key = "0x" + key
    return Account.from_key(key)


def get_default_address() -> Optional[str]:
    """获取默认测试账户地址。"""
    try:
        return get_account().address
    except Exception:
        return None
