# Web3 自动化测试框架 - Claude 指令

## 项目概述

这是一个企业级 Web3 自动化测试框架，位于 `/Users/mayuming/Desktop/web3-auto-test/`。

### 技术栈

**区块链开发环境：**
- Hardhat 3.4.5 (ESM 模式)
- Solidity 0.8.27
- OpenZeppelin Contracts 5.6.1
- Ethers.js 6.16.0

**Python 测试框架：**
- Python 3.11+
- pytest 8.3.4
- Web3.py 7.6.0
- Playwright 1.49.1
- Allure 2.29.1

**已实现的测试集：**
1. **NFT Mint DApp** - NFT 铸造、转账、授权测试
2. **DEX Swap** - 去中心化交易所、流动性池、代币兑换测试
3. **Staking** - 质押挖矿、奖励分配、锁定期测试
4. **Wallet Security** - 钱包签名、EIP-2612 Permit、授权安全测试

### 核心架构原则

**四层架构设计：**
1. **framework/** - 原子能力层，提供通用工具类，不包含业务逻辑
2. **tests/*/apis/** - 单接口层，封装单个合约接口调用
3. **tests/*/fixtures/** - 场景层，通过 pytest fixtures 组装多个接口
4. **tests/*/scenarios/** - 测试层，执行场景测试

**关键原则：**
- framework 封装原子能力，与业务接口无关
- 单接口是构建块，只负责调用和返回，不包含断言
- 场景通过 fixtures 组装，可以包含断言和验证逻辑
- 测试用例执行场景，验证结果

### Web3 客户端架构

框架提供多种调用方式，适配不同使用场景：

**1. Web3Client** - 直接 Web3.py 封装
```python
from framework.web3 import Web3Client

client = Web3Client("http://127.0.0.1:8545")
contract = client.load_contract(address, abi)
tx_hash = client.send_contract_transaction(contract, "transfer", account, to, amount)
```

**2. EthersClient** - Ethers.js 风格 API
```python
from framework.web3 import EthersClient

client = EthersClient("http://127.0.0.1:8545")
amount = client.parse_ether("1.0")  # 转换为 Wei
balance = client.format_ether(wei_amount)  # 转换为 Ether
```

**3. HardhatClient** - Hardhat 集成
```python
from framework.web3 import HardhatClient

client = HardhatClient()
address = client.deploy_contract("MyContract", [arg1, arg2])
signers = client.get_signers(10)  # 获取测试账户
```

**4. RPCClient** - JSON-RPC 调用
```python
from framework.web3 import RPCClient

client = RPCClient("http://127.0.0.1:8545")
result = client.call("eth_blockNumber", [])
client.mine_blocks(10)  # 挖矿
client.increase_time(86400)  # 快进时间
```

**5. WalletSigner** - 钱包签名
```python
from framework.web3 import WalletSigner

signer = WalletSigner(account)
# EIP-712 结构化数据签名
sig = signer.sign_typed_data(typed_data)
# EIP-2612 Permit 签名
permit_sig = signer.sign_permit(token_address, token_name, owner, spender, value, nonce, deadline)
# 个人消息签名
personal_sig = signer.sign_personal_message("Hello World")
```

## 快速生成测试用例

### 1. 智能合约测试用例生成

当用户要求生成智能合约测试用例时：

**步骤：**
1. 在 `contracts/` 下创建或查看合约代码
2. 在 `tests/*/apis/` 下创建合约 API 封装
3. 在 `tests/*/fixtures/` 中创建场景 fixture
4. 在 `tests/*/scenarios/` 下创建测试文件

**模板：**
```python
# tests/nft_mint/apis/nft_contract_api.py
class NFTContractAPI:
    def __init__(self, web3_client, contract_address, abi):
        self.client = web3_client
        self.contract = web3_client.load_contract(contract_address, abi)
        self.address = contract_address

    def mint(self, to, uri, from_account, value=None):
        """铸造 NFT"""
        return self.client.send_contract_transaction(
            self.contract, "mint", from_account, to, uri, value=value
        )

    def balance_of(self, address):
        """查询余额"""
        return self.client.call_contract_function(self.contract, "balanceOf", address)

# tests/nft_mint/fixtures/nft_fixtures.py
@pytest.fixture(scope="session")
def nft_deployed(hardhat_client):
    """场景：部署 NFT 合约"""
    with allure.step("部署 NFT 合约"):
        address = hardhat_client.deploy_contract(
            "MockERC721",
            ["Test NFT", "TNFT", 10000, web3_client.to_wei(0.01, 'ether')]
        )
        assert address, "NFT 合约部署失败"

    abi, _ = hardhat_client.load_contract_artifact("MockERC721")
    return {'address': address, 'abi': abi}

@pytest.fixture(scope="function")
def minted_nft(nft_api, user1, web3_client):
    """场景：铸造 NFT"""
    token_uri = f"ipfs://QmTest{TestDataFactory.unique_id()}"
    mint_price = nft_api.mint_price()

    with allure.step("铸造 NFT"):
        tx_hash = nft_api.mint(user1.address, token_uri, user1, value=mint_price)
        receipt = web3_client.wait_for_transaction_receipt(tx_hash)
        assert receipt['status'] == 1

    return {'token_id': 0, 'token_uri': token_uri, 'owner': user1.address}

# tests/nft_mint/scenarios/test_nft_scenario.py
@allure.feature("NFT Mint")
@allure.story("NFT 铸造场景")
class TestNFTScenario:
    def test_mint_nft_scenario(self, minted_nft, nft_api):
        """场景：铸造 NFT"""
        with allure.step("验证 NFT 所有权"):
            owner = nft_api.owner_of(minted_nft['token_id'])
            assert owner == minted_nft['owner']

        with allure.step("验证 Token URI"):
            uri = nft_api.token_uri(minted_nft['token_id'])
            assert uri == minted_nft['token_uri']
```

### 2. DEX/DeFi 测试用例生成

当用户要求生成 DEX 或 DeFi 测试用例时：

**步骤：**
1. 在 `tests/dex_swap/apis/` 下创建 DEX 和 ERC20 API
2. 在 `tests/dex_swap/fixtures/` 中创建流动性、交易场景
3. 在 `tests/dex_swap/scenarios/` 下创建测试文件

**模板：**
```python
# tests/dex_swap/apis/dex_api.py
class DEXAPI:
    def add_liquidity(self, token_a, token_b, amount_a, amount_b, from_account):
        """添加流动性"""
        return self.client.send_contract_transaction(
            self.contract, "addLiquidity", from_account,
            token_a, token_b, amount_a, amount_b
        )

    def swap(self, token_in, token_out, amount_in, min_amount_out, from_account):
        """代币兑换"""
        return self.client.send_contract_transaction(
            self.contract, "swap", from_account,
            token_in, token_out, amount_in, min_amount_out
        )

# tests/dex_swap/fixtures/dex_fixtures.py
@pytest.fixture(scope="function")
def liquidity_added(dex_api, token_a_api, token_b_api, user1, web3_client):
    """场景：添加流动性"""
    amount_a = web3_client.to_wei(1000, 'ether')
    amount_b = web3_client.to_wei(2000, 'ether')

    with allure.step("授权代币"):
        token_a_api.approve(dex_api.address, amount_a, user1)
        token_b_api.approve(dex_api.address, amount_b, user1)

    with allure.step("添加流动性"):
        tx_hash = dex_api.add_liquidity(
            token_a_api.address, token_b_api.address,
            amount_a, amount_b, user1
        )
        receipt = web3_client.wait_for_transaction_receipt(tx_hash)
        assert receipt['status'] == 1

    return {'amount_a': amount_a, 'amount_b': amount_b}

# tests/dex_swap/scenarios/test_dex_scenario.py
def test_swap_scenario(dex_api, liquidity_added, token_a_api, user2, web3_client):
    """场景：代币兑换"""
    swap_amount = web3_client.to_wei(100, 'ether')

    with allure.step("执行兑换"):
        tx_hash = dex_api.swap(
            token_a_api.address, token_b_api.address,
            swap_amount, 0, user2
        )
        receipt = web3_client.wait_for_transaction_receipt(tx_hash)
        assert receipt['status'] == 1
```

### 3. Staking 测试用例生成

当用户要求生成质押挖矿测试用例时：

**模板：**
```python
# tests/staking/apis/staking_api.py
class StakingAPI:
    def stake(self, amount, from_account):
        """质押代币"""
        return self.client.send_contract_transaction(
            self.contract, "stake", from_account, amount
        )

    def earned(self, address):
        """查询已赚取的奖励"""
        return self.client.call_contract_function(self.contract, "earned", address)

    def get_reward(self, from_account):
        """领取奖励"""
        return self.client.send_contract_transaction(
            self.contract, "getReward", from_account
        )

# tests/staking/fixtures/staking_fixtures.py
@pytest.fixture(scope="function")
def user_staked(staking_api, staking_token_api, user1, web3_client):
    """场景：用户质押代币"""
    stake_amount = web3_client.to_wei(1000, 'ether')

    with allure.step("授权质押代币"):
        staking_token_api.approve(staking_api.address, stake_amount, user1)

    with allure.step("质押代币"):
        tx_hash = staking_api.stake(stake_amount, user1)
        receipt = web3_client.wait_for_transaction_receipt(tx_hash)
        assert receipt['status'] == 1

    return {'user': user1.address, 'amount': stake_amount}

# tests/staking/scenarios/test_staking_scenario.py
def test_reward_calculation_scenario(staking_api, user_staked, rpc_client):
    """场景：奖励计算"""
    with allure.step("等待累积奖励"):
        time.sleep(5)
        rpc_client.mine_blocks(5)

    with allure.step("查询已赚取的奖励"):
        earned = staking_api.earned(user_staked['user'])
        assert earned > 0, "奖励应该大于 0"
```

### 4. 钱包签名安全测试用例生成

当用户要求生成钱包签名或授权安全测试时：

**模板：**
```python
# tests/wallet_security/apis/wallet_api.py
class WalletAPI:
    def generate_permit_signature(self, owner_account, spender, value, deadline):
        """生成 Permit 签名 (EIP-2612)"""
        signer = WalletSigner(owner_account)
        nonce = self.nonces(owner_account.address)

        return signer.sign_permit(
            token_address=self.address,
            token_name=self.name(),
            owner=owner_account.address,
            spender=spender,
            value=value,
            nonce=nonce,
            deadline=deadline
        )

    def permit(self, owner, spender, value, deadline, v, r, s, from_account):
        """使用签名授权"""
        return self.client.send_contract_transaction(
            self.contract, "permit", from_account,
            owner, spender, value, deadline, v, r, s
        )

# tests/wallet_security/fixtures/wallet_fixtures.py
@pytest.fixture(scope="function")
def permit_signature_generated(wallet_api, user1, spender, web3_client):
    """场景：生成 Permit 签名"""
    value = web3_client.to_wei(500, 'ether')
    deadline = int(time.time()) + 3600

    with allure.step("生成 Permit 签名"):
        signature_data = wallet_api.generate_permit_signature(
            owner_account=user1,
            spender=spender.address,
            value=value,
            deadline=deadline
        )

    return {
        'owner': user1.address,
        'spender': spender.address,
        'value': value,
        'deadline': deadline,
        'signature': signature_data
    }

# tests/wallet_security/scenarios/test_wallet_security_scenario.py
def test_permit_authorization_scenario(wallet_api, permit_signature_generated, spender, web3_client):
    """场景：使用 Permit 授权"""
    permit_data = permit_signature_generated
    sig = permit_data['signature']

    with allure.step("执行 Permit 授权"):
        tx_hash = wallet_api.permit(
            permit_data['owner'], permit_data['spender'],
            permit_data['value'], permit_data['deadline'],
            sig['v'], sig['r'], sig['s'], spender
        )
        receipt = web3_client.wait_for_transaction_receipt(tx_hash)
        assert receipt['status'] == 1

    with allure.step("验证授权额度"):
        allowance = wallet_api.allowance(permit_data['owner'], permit_data['spender'])
        assert allowance == permit_data['value']
```

## 常用工具类

### Web3 客户端工具

**Web3Client** - 核心 Web3 操作
```python
from framework.web3 import Web3Client

client = Web3Client("http://127.0.0.1:8545")

# 单位转换
wei = client.to_wei(1.0, 'ether')
ether = client.from_wei(wei, 'ether')

# 合约操作
contract = client.load_contract(address, abi)
result = client.call_contract_function(contract, "balanceOf", address)
tx_hash = client.send_contract_transaction(contract, "transfer", account, to, amount)

# 交易处理
receipt = client.wait_for_transaction_receipt(tx_hash, timeout=120)
block = client.get_block('latest')
```

**HardhatClient** - Hardhat 集成
```python
from framework.web3 import HardhatClient

client = HardhatClient()

# 合约部署
address = client.deploy_contract("MyContract", [arg1, arg2], deployer=account)

# 加载合约
abi, bytecode = client.load_contract_artifact("MyContract")

# 获取测试账户
signers = client.get_signers(10)
owner = signers[0]
```

**RPCClient** - JSON-RPC 操作
```python
from framework.web3 import RPCClient

client = RPCClient("http://127.0.0.1:8545")

# RPC 调用
result = client.call("eth_blockNumber", [])

# 测试辅助
client.mine_blocks(10)  # 挖 10 个块
client.increase_time(86400)  # 快进 1 天
client.snapshot()  # 创建快照
client.revert(snapshot_id)  # 恢复快照
```

**WalletSigner** - 钱包签名
```python
from framework.web3 import WalletSigner

signer = WalletSigner(account)

# EIP-2612 Permit 签名
permit_sig = signer.sign_permit(
    token_address=token_address,
    token_name="MyToken",
    owner=owner_address,
    spender=spender_address,
    value=amount,
    nonce=0,
    deadline=deadline,
    chain_id=31337
)

# EIP-712 结构化数据签名
typed_sig = signer.sign_typed_data(typed_data)

# 个人消息签名
personal_sig = signer.sign_personal_message("Hello World")

# 恢复签名者
recovered = signer.recover_signer(message, signature)
```

### 测试数据生成

**TestDataFactory** - 测试数据生成
```python
from framework.utils import TestDataFactory

factory = TestDataFactory()

# 基础数据
unique_id = factory.unique_id()
timestamp = factory.timestamp()

# 用户数据
username = factory.unique_username()
email = factory.unique_email()
password = factory.random_password()

# Web3 数据
wallet_address = factory.unique_wallet_address()
tx_hash = factory.random_tx_hash()
token_amount = factory.random_token_amount(decimals=18)

# 完整数据
user_data = TestDataFactory.create_user_data()
tx_data = TestDataFactory.create_transaction_data()
```

### 验证工具

**RPCValidator** - RPC 响应验证
```python
from framework.utils import RPCValidator

validator = RPCValidator()

# 验证响应
assert validator.validate_rpc_response(response)

# 提取结果
result = validator.extract_rpc_result(response)

# 验证字段
assert validator.validate_field_exists(result, 'hash')
assert validator.validate_field_type(result, 'number', str)
```

### 重试和轮询

**RetryHelper** - 重试机制
```python
from framework.utils import RetryHelper, retry_on_failure

# 装饰器方式
@retry_on_failure(max_retries=3, delay=1.0, backoff=2.0)
def unstable_operation():
    # 可能失败的操作
    pass

# 手动方式
helper = RetryHelper(max_retries=3, delay=1.0)
result = helper.retry(lambda: api.call())
```

**PollingHelper** - 轮询机制
```python
from framework.utils import PollingHelper

helper = PollingHelper()

# 轮询交易回执
receipt = helper.poll_transaction_receipt(
    get_receipt_func,
    tx_hash,
    timeout=120.0,
    interval=3.0
)

# 轮询直到条件满足
result = helper.poll_until(
    check_func,
    condition=lambda x: x is not None,
    timeout=60.0
)
```

## 代码规范

### 命名规范
- 测试文件：`test_*_scenario.py`
- 测试类：`Test*Scenario`
- 测试方法：`test_*_scenario`
- Fixture：描述性名称，如 `logged_in_user`, `latest_block`

### Allure 报告
```python
@allure.feature("功能模块")
@allure.story("业务场景")
class TestScenario:
    def test_scenario(self):
        with allure.step("步骤描述"):
            # 操作
            pass
```

### 断言规范
```python
# ✅ 好的做法：清晰的断言消息
assert block_number, "区块号不能为空"
assert response.status_code == 200, f"请求失败: {response.status_code}"

# ✅ 好的做法：使用验证器
assert validator.validate_rpc_response(response)

# ❌ 避免：模糊的断言
assert block_number
```

## 注意事项

### 架构规范
1. **不要在 framework/ 中写业务逻辑** - framework 只提供通用工具
2. **单接口不包含断言，只负责调用** - API 层只封装调用逻辑
3. **场景 fixture 可以包含断言和验证** - 场景层负责组装和验证
4. **测试用例执行场景，验证结果** - 测试层关注业务场景

### 测试数据
5. **使用 TestDataFactory 生成测试数据，避免硬编码**
6. **敏感信息放在 .env，非敏感信息放在 config/*.yaml**

### 报告和日志
7. **使用 Allure 装饰器和 step 增强报告可读性**
8. **使用 logger 记录关键操作和结果**

### 异步和重试
9. **处理异步操作使用 PollingHelper 或 RetryHelper**
10. **等待交易确认使用 wait_for_transaction_receipt**
11. **测试时间相关逻辑使用 rpc_client.increase_time() 快进时间**

### Hardhat 集成
12. **合约部署使用 HardhatClient.deploy_contract()**
13. **测试账户使用 HardhatClient.get_signers()**
14. **合约编译后自动生成 artifacts，无需手动管理**

### 签名安全
15. **EIP-2612 Permit 签名使用 WalletSigner.sign_permit()**
16. **EIP-712 结构化数据签名使用 WalletSigner.sign_typed_data()**
17. **验证签名使用 WalletSigner.recover_signer()**

## 快速命令

### Hardhat 命令
```bash
# 启动本地节点
npx hardhat node

# 编译合约
npx hardhat compile

# 清理编译产物
npx hardhat clean
```

### 测试命令
```bash
# 运行 NFT Mint 测试
pytest tests/nft_mint/scenarios/ -v

# 运行 DEX Swap 测试
pytest tests/dex_swap/scenarios/ -v

# 运行 Staking 测试
pytest tests/staking/scenarios/ -v

# 运行 Wallet Security 测试
pytest tests/wallet_security/scenarios/ -v

# 运行所有测试
pytest tests/ -v

# 生成 Allure 报告
pytest --alluredir=allure-results
allure serve allure-results

# 运行示例
pytest examples/ -v
```

### 调试命令
```bash
# 运行单个测试
pytest tests/nft_mint/scenarios/test_nft_scenario.py::TestNFTScenario::test_mint_nft_scenario -v

# 显示详细输出
pytest tests/nft_mint/scenarios/ -v -s

# 失败时进入调试
pytest tests/nft_mint/scenarios/ --pdb

# 只运行失败的测试
pytest --lf
```

## 项目结构

```
web3-auto-test/
├── contracts/                  # Solidity 智能合约
│   ├── MockERC20.sol          # ERC20 代币合约
│   ├── MockERC20Permit.sol    # 支持 Permit 的 ERC20
│   ├── MockERC721.sol         # ERC721 NFT 合约
│   ├── SimpleDEX.sol          # 简单 DEX 合约
│   └── StakingPool.sol        # 质押池合约
├── framework/                  # 框架层（原子能力）
│   ├── web3/                  # Web3 客户端封装
│   │   ├── web3_client.py     # Web3.py 封装
│   │   ├── ethers_client.py   # Ethers.js 风格 API
│   │   ├── hardhat_client.py  # Hardhat 集成
│   │   ├── rpc_client.py      # JSON-RPC 客户端
│   │   └── wallet_signer.py   # 钱包签名工具
│   ├── utils/                 # 工具类
│   │   ├── test_data_factory.py  # 测试数据生成
│   │   ├── rpc_validator.py      # RPC 验证器
│   │   ├── retry_helper.py       # 重试机制
│   │   └── polling_helper.py     # 轮询机制
│   └── core/                  # 核心工具
│       └── logger.py          # 日志工具
├── tests/                     # 测试集
│   ├── nft_mint/             # NFT 铸造测试
│   │   ├── apis/             # NFT 合约 API
│   │   ├── fixtures/         # NFT 场景 fixtures
│   │   ├── scenarios/        # NFT 测试场景
│   │   └── conftest.py       # pytest 配置
│   ├── dex_swap/             # DEX 交易测试
│   │   ├── apis/             # DEX 和 ERC20 API
│   │   ├── fixtures/         # DEX 场景 fixtures
│   │   ├── scenarios/        # DEX 测试场景
│   │   └── conftest.py
│   ├── staking/              # 质押挖矿测试
│   │   ├── apis/             # Staking API
│   │   ├── fixtures/         # Staking 场景 fixtures
│   │   ├── scenarios/        # Staking 测试场景
│   │   └── conftest.py
│   └── wallet_security/      # 钱包安全测试
│       ├── apis/             # Wallet API
│       ├── fixtures/         # Wallet 场景 fixtures
│       ├── scenarios/        # Wallet 测试场景
│       └── conftest.py
├── config/                    # 配置文件
│   └── test_config.yaml      # 测试配置
├── hardhat.config.js         # Hardhat 配置
├── package.json              # Node.js 依赖
├── requirements.txt          # Python 依赖
├── pytest.ini                # pytest 配置
└── .env                      # 环境变量
```