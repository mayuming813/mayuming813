"""
合约加载器：根据合约名与地址加载 ABI 并返回可调用合约实例。
"""
import json
from pathlib import Path
from typing import Any, Dict, Optional

from web3 import Web3
from web3.contract import Contract

from config import settings


def load_abi(contract_name: str) -> list:
    """
    从 contracts/abi/{contract_name}.json 加载 ABI。
    @param contract_name 合约名（文件名不含后缀）
    @return ABI 列表
    """
    path = settings.abi_dir / f"{contract_name}.json"
    if not path.exists():
        raise FileNotFoundError(f"ABI not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "abi" in data:
        return data["abi"]
    return data


def get_contract(
    w3: Web3,
    contract_name: str,
    address: Optional[str] = None,
    abi_override: Optional[list] = None,
) -> Contract:
    """
    获取合约实例。
    @param w3 Web3 实例
    @param contract_name 合约名（用于加载 ABI 及从配置取地址）
    @param address 合约地址，若为 None 则尝试从 settings 或 env 读取
    @param abi_override 若提供则不用文件 ABI
    @return Contract 实例
    """
    abi = abi_override or load_abi(contract_name)
    addr = address or _contract_address(contract_name)
    if not addr:
        raise ValueError(f"Contract address not set for: {contract_name}")
    return w3.eth.contract(address=Web3.to_checksum_address(addr), abi=abi)


def _contract_address(contract_name: str) -> Optional[str]:
    """从环境或 yaml 读取合约地址。"""
    env_key = f"CONTRACT_ADDRESS_{contract_name.upper()}"
    import os
    addr = os.environ.get(env_key) or getattr(settings, "contract_address", None)
    if addr:
        return addr
    yaml_cfg = settings.load_yaml()
    contracts = yaml_cfg.get("contracts") or {}
    return contracts.get(contract_name)
