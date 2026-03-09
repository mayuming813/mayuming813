#!/usr/bin/env python3
"""
查询当前钱包账户余额，用于验证与本地 MetaMask 的联动。
使用 .env 中的 WALLET_ADDRESS / TEST_PRIVATE_KEY 与 ETH_RPC_URL，查询链上余额并与 MetaMask 显示对比。
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def main():
    from dotenv import load_dotenv
    from web3 import Web3

    load_dotenv(ROOT / ".env")

    rpc_url = os.environ.get("ETH_RPC_URL", "https://ethereum-sepolia.publicnode.com")
    wallet_address = os.environ.get("WALLET_ADDRESS", "").strip()
    private_key = os.environ.get("TEST_PRIVATE_KEY", "").strip()

    # 确定要查询的地址：优先用私钥推导（与部署账户一致），并与 WALLET_ADDRESS 校验
    if private_key:
        from eth_account import Account
        if not private_key.startswith("0x"):
            private_key = "0x" + private_key
        account = Account.from_key(private_key)
        address = account.address
        if wallet_address and address.lower() != wallet_address.lower():
            print(f"校验: 私钥对应地址 {address} 与 .env 中 WALLET_ADDRESS {wallet_address} 不一致")
        else:
            print(f"校验: 私钥对应地址与 WALLET_ADDRESS 一致（本地 MetaMask 联动）")
    elif wallet_address:
        address = wallet_address if wallet_address.startswith("0x") else "0x" + wallet_address
        print("未配置 TEST_PRIVATE_KEY，仅按 WALLET_ADDRESS 查询余额")
    else:
        print("请在 .env 中配置 WALLET_ADDRESS 或 TEST_PRIVATE_KEY")
        sys.exit(1)

    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        print(f"无法连接 RPC: {rpc_url}")
        sys.exit(1)

    balance_wei = w3.eth.get_balance(address)
    balance_eth = w3.from_wei(balance_wei, "ether")
    chain_id = w3.eth.chain_id

    print()
    print("--- 当前钱包账户（与 MetaMask 对比）---")
    print(f"  地址:     {address}")
    print(f"  链 ID:    {chain_id}")
    print(f"  余额:     {balance_wei} wei")
    print(f"  余额:     {balance_eth} ETH")
    print()
    print("请在 MetaMask 中切换到同一网络，查看该地址余额是否一致。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
