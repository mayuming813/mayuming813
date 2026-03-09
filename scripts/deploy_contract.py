#!/usr/bin/env python3
"""
全程代码：从 .env 读取 TEST_PRIVATE_KEY 发起部署，无需在 MetaMask 中操作。
测试过程中如需查看链上数据，可打开 MetaMask 查看余额、活动等。
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def deploy_with_key(rpc_url: str, chain_id: int, private_key: str, contract_name: str = "SepoliaClaimFaucet"):
    """使用私钥部署，返回合约地址。"""
    from eth_account import Account
    from web3 import Web3

    build_path = ROOT / "contracts" / "build" / f"{contract_name}.json"
    if not build_path.exists():
        raise FileNotFoundError(f"请先运行编译: python scripts/compile_contract.py\n  {build_path} 不存在")

    with open(build_path, "r", encoding="utf-8") as f:
        build = json.load(f)
    abi = build["abi"]
    bytecode = build["bytecode"]

    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        raise RuntimeError(f"无法连接 RPC: {rpc_url}")

    key = private_key.strip()
    if not key.startswith("0x"):
        key = "0x" + key
    account = Account.from_key(key)

    nonce = w3.eth.get_transaction_count(account.address)
    contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    tx = contract.constructor().build_transaction({
        "from": account.address,
        "chainId": chain_id,
        "nonce": nonce,
        "gas": 2_000_000,
    })
    try:
        tx["gas"] = w3.eth.estimate_gas(tx)
    except Exception:
        pass

    signed = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    if receipt["status"] != 1:
        raise RuntimeError("部署交易失败")
    contract_address = receipt["contractAddress"]
    return contract_address, tx_hash.hex()


def main():
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
    import os
    from eth_account import Account

    parser = argparse.ArgumentParser(description="部署 SepoliaClaimFaucet 合约（与本地 MetaMask 钱包联动）")
    parser.add_argument("--rpc", default=os.environ.get("ETH_RPC_URL", "https://ethereum-sepolia.publicnode.com"), help="RPC URL（Infura 需用 https://sepolia.infura.io/v3/项目ID）")
    parser.add_argument("--chain-id", type=int, default=int(os.environ.get("CHAIN_ID", "11155111")), help="Chain ID")
    parser.add_argument("--key", default=os.environ.get("TEST_PRIVATE_KEY"), help="部署账户私钥（不填则从 .env 读）")
    parser.add_argument("--wallet-address", default=os.environ.get("WALLET_ADDRESS"), help="本地 MetaMask 地址，用于校验私钥对应同一账户")
    args = parser.parse_args()

    if not args.key:
        print("未设置私钥。请在 .env 中配置 TEST_PRIVATE_KEY（从 MetaMask 导出该账户私钥），或使用 --key。")
        sys.exit(1)

    key = args.key.strip()
    if not key.startswith("0x"):
        key = "0x" + key
    account = Account.from_key(key)
    deployer_address = account.address

    # 若配置了本地钱包地址，校验私钥与该地址一致，确保联动的是同一 MetaMask 账户
    if args.wallet_address:
        expected = args.wallet_address.strip()
        if expected.startswith("0x"):
            expected = expected[2:]
        if deployer_address.lower() != ("0x" + expected).lower():
            print(f"私钥对应地址与本地钱包不一致，无法联动。")
            print(f"  当前私钥对应: {deployer_address}")
            print(f"  配置的 WALLET_ADDRESS: {args.wallet_address}")
            print("请在 MetaMask 中导出账户 0xb1D0Ff0982D3b700eBE0b1861be6e6514e1f6164 的私钥，填入 .env 的 TEST_PRIVATE_KEY。")
            sys.exit(1)
        print(f"部署账户（与本地 MetaMask 联动）: {deployer_address}")

    try:
        address, tx_hash = deploy_with_key(args.rpc, args.chain_id, args.key)
        print()
        print("部署成功")
        print(f"  合约地址:   {address}")
        print(f"  交易哈希:   {tx_hash}")
        print(f"  部署账户:   {deployer_address} （可在 MetaMask 中查看该账户的余额与活动）")
        print()
        print(f"请将 CONTRACT_ADDRESS={address} 写入 .env")
    except Exception as e:
        print(f"部署失败: {e}")
        sys.exit(1)

    return 0


if __name__ == "__main__":
    sys.exit(main())
