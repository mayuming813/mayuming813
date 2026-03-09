"""
配置加载：从环境变量与 yaml 读取测试相关配置。
"""
import os
from pathlib import Path
from typing import Optional

import yaml
from dotenv import load_dotenv

load_dotenv()

# 项目根目录
ROOT_DIR = Path(__file__).resolve().parent.parent


def _env(key: str, default: Optional[str] = None) -> Optional[str]:
    return os.environ.get(key, default)


class Settings:
    """测试工程配置。"""

    # 链配置
    eth_rpc_url: str = _env("ETH_RPC_URL") or "http://127.0.0.1:8545"
    chain_id: int = int(_env("CHAIN_ID") or "1337")
    test_private_key: Optional[str] = _env("TEST_PRIVATE_KEY")

    # 合约（后续按合约名扩展）
    contract_address: Optional[str] = _env("CONTRACT_ADDRESS")

    # UI 与 API（pynpress 每次用助记词导入 MetaMask）
    wallet_extension_path: Optional[str] = _env("WALLET_EXTENSION_PATH")
    metamask_extension_id: str = _env("METAMASK_EXTENSION_ID") or "nkbihfbeogaeaoehlefnkodbefgpgknn"
    # 助记词与解锁密码（必填，用于 pynpress 导入钱包）
    metamask_seed_phrase: str = _env("METAMASK_SEED_PHRASE") or _env("MNEMONIC") or ""
    metamask_password: str = _env("METAMASK_PASSWORD") or "TestPassword123!"
    base_url: str = _env("BASE_URL") or "http://localhost:3000"
    api_base_url: str = _env("API_BASE_URL") or "http://localhost:8080"

    # 路径
    contracts_dir: Path = ROOT_DIR / "contracts"
    abi_dir: Path = ROOT_DIR / "contracts" / "abi"

    @classmethod
    def load_yaml(cls, path: Optional[Path] = None) -> dict:
        """加载 config 目录下的 yaml 配置（可选）。"""
        config_path = path or ROOT_DIR / "config" / "env.yaml"
        if not config_path.exists():
            return {}
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}


settings = Settings()
