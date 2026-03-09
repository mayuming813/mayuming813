"""
Pytest 公共 fixture：Web3 连接、账户、合约、链 API 等。
"""
import pytest
from web3 import Web3

from config import settings
from contracts import get_contract, load_abi
from utils import get_w3, get_account, ChainApiClient


@pytest.fixture(scope="session")
def w3() -> Web3:
    """会话级 Web3 实例。"""
    return get_w3()


@pytest.fixture(scope="session")
def chain_id() -> int:
    return settings.chain_id


@pytest.fixture
def chain_api(w3: Web3) -> ChainApiClient:
    """链上接口测试客户端。"""
    return ChainApiClient(w3)


@pytest.fixture
def tester_account():
    """测试账户（需配置 TEST_PRIVATE_KEY）。"""
    try:
        return get_account()
    except ValueError as e:
        pytest.skip(f"TEST_PRIVATE_KEY not set: {e}")


@pytest.fixture
def tester_address(tester_account):
    return tester_account.address


def _contract_factory(name: str):
    """返回合约名对应的 fixture：合约实例。"""
    @pytest.fixture
    def _contract(w3: Web3):
        try:
            return get_contract(w3, name)
        except (FileNotFoundError, ValueError) as e:
            pytest.skip(f"Contract {name} not available: {e}")
    return _contract


@pytest.fixture(scope="session")
def faucet_contract(w3: Web3):
    """SepoliaClaimFaucet 合约实例（需在 .env 中配置 CONTRACT_ADDRESS）。"""
    try:
        return get_contract(w3, "SepoliaClaimFaucet")
    except (FileNotFoundError, ValueError) as e:
        pytest.skip(f"SepoliaClaimFaucet 不可用（请先编译并部署，配置 CONTRACT_ADDRESS）: {e}")
