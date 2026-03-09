"""
Raw JSON-RPC 客户端：直接对 ETH_RPC_URL 发起 eth_* / net_* / web3_* 请求，用于接口自动化。
"""
import json
from typing import Any, Dict, List, Optional, Union

import requests

from config import settings


def rpc_call(
    method: str,
    params: Optional[List[Any]] = None,
    rpc_url: Optional[str] = None,
    timeout: int = 30,
) -> Any:
    """
    发送 JSON-RPC 2.0 请求，返回 result 字段；若存在 error 则抛出异常。
    @param method 方法名，如 eth_blockNumber, eth_getBalance
    @param params 参数列表
    @param rpc_url 不填则用 settings.eth_rpc_url
    @param timeout 请求超时秒数
    @return 响应中的 result
    """
    url = rpc_url or settings.eth_rpc_url
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params if params is not None else [],
        "id": 1,
    }
    resp = requests.post(url, json=payload, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()
    if "error" in data:
        err = data["error"]
        raise RuntimeError(f"JSON-RPC error: {err.get('message', err)} (code={err.get('code')})")
    return data.get("result")


def eth_block_number(rpc_url: Optional[str] = None) -> int:
    """eth_blockNumber -> 十六进制，转为 int 返回。"""
    raw = rpc_call("eth_blockNumber", rpc_url=rpc_url)
    return int(raw, 16)


def eth_chain_id(rpc_url: Optional[str] = None) -> int:
    """eth_chainId -> 十六进制，转为 int。"""
    raw = rpc_call("eth_chainId", rpc_url=rpc_url)
    return int(raw, 16)


def eth_get_balance(address: str, block: str = "latest", rpc_url: Optional[str] = None) -> int:
    """eth_getBalance(address, block) -> wei (int)。"""
    raw = rpc_call("eth_getBalance", [address, block], rpc_url=rpc_url)
    return int(raw, 16)


def eth_get_block_by_number(
    block: Union[str, int],
    full_tx: bool = False,
    rpc_url: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    eth_getBlockByNumber(block, full_tx)。
    block 可为 "latest"/"pending"/"earliest" 或区块号 (int)。
    """
    if isinstance(block, int):
        block_hex = hex(block)
    else:
        block_hex = block
    return rpc_call("eth_getBlockByNumber", [block_hex, full_tx], rpc_url=rpc_url)


def eth_gas_price(rpc_url: Optional[str] = None) -> int:
    """eth_gasPrice -> wei (int)。"""
    raw = rpc_call("eth_gasPrice", rpc_url=rpc_url)
    return int(raw, 16)


def net_version(rpc_url: Optional[str] = None) -> str:
    """net_version -> 链 ID 字符串。"""
    return str(rpc_call("net_version", rpc_url=rpc_url))


def web3_client_version(rpc_url: Optional[str] = None) -> str:
    """web3_clientVersion。"""
    return str(rpc_call("web3_clientVersion", rpc_url=rpc_url))
