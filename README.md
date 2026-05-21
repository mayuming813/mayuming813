# Web3 自动化测试框架

企业级 Web3 测试框架，支持智能合约单元测试、API 测试、RPC 测试、UI 测试和对账功能。

## 🚀 核心特性

- ✅ **四层架构**：framework（原子能力）→ APIs（单接口）→ Fixtures（场景组装）→ Scenarios（测试执行）
- ✅ **智能合约测试**：支持 NFT、ERC20、DEX、Staking、Wallet Security 等场景
- ✅ **多客户端支持**：Hardhat、Web3.py、Ethers.js、Ape、Brownie
- ✅ **EIP 标准支持**：EIP-2612 Permit、EIP-712 签名、EIP-1559 交易
- ✅ **场景化测试**：通过 pytest fixtures 灵活组装测试场景
- ✅ **失败重试**：支持动态配置重试次数和策略
- ✅ **异步轮询**：处理链上异步数据，支持轮询直到满足条件
- ✅ **对账功能**：支持实时/T+0/T+1 对账，自动处理链上异步数据
- ✅ **测试数据工厂**：丰富的测试数据生成能力，避免并发冲突
- ✅ **Allure 报告**：详细的测试报告，包含请求/响应/步骤信息
- ✅ **UI 增强**：失败自动截图/录屏，支持严格/软断言
- ✅ **配置安全**：敏感信息存储在 .env，不提交仓库

## 📋 技术栈

### 后端测试
- **Python**: 3.11+
- **Pytest**: 8.3.4 - 测试框架
- **Web3.py**: 7.6.0 - 以太坊 Python 客户端
- **eth-account**: 0.14.0 - 账户管理和签名
- **Allure**: 2.13.5 - 测试报告

### 智能合约
- **Node.js**: 22.13.0+
- **Hardhat**: 3.4.5 - 智能合约开发环境
- **Solidity**: 0.8.27
- **OpenZeppelin Contracts**: 5.6.1
- **Ethers.js**: 6.16.0

### UI 测试
- **Playwright**: 1.49.1 - 浏览器自动化
- **Playwright-pytest**: 0.6.2

### 其他工具
- **Requests**: 2.32.3 - HTTP 客户端
- **PyYAML**: 6.0.2 - 配置管理
- **python-dotenv**: 1.0.1 - 环境变量管理

## ⚡ 快速开始

### 1. 环境准备

**安装 Node.js 22.13.0+**
```bash
# 使用 nvm 安装
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 22.13.0
nvm use 22.13.0
```

**安装 Python 3.11+**
```bash
# macOS
brew install python@3.11

# Ubuntu
sudo apt install python3.11 python3.11-venv
```

**安装项目依赖**
```bash
# Python 依赖
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Playwright 浏览器
playwright install chromium

# Node.js 依赖
npm install
```

### 2. 配置环境

```bash
# 复制配置模板
cp .env.example .env
cp config/config.example.yaml config/local.yaml

# 编辑 .env 填入敏感信息
vim .env
```

**.env 示例**
```bash
# Hardhat 本地网络
HARDHAT_RPC_URL=http://127.0.0.1:8545
HARDHAT_CHAIN_ID=31337

# 测试账户私钥（Hardhat 默认账户）
TEST_PRIVATE_KEY=0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80

# API 配置
API_BASE_URL=http://localhost:3000
API_TIMEOUT=30
```

### 3. 启动 Hardhat 节点

```bash
# 终端 1：启动 Hardhat 本地节点
npx hardhat node

# 终端 2：编译合约
npx hardhat compile
```

### 4. 运行测试

```bash
# 激活虚拟环境
source venv/bin/activate

# 运行所有智能合约测试
pytest tests/nft_mint/scenarios/ -v
pytest tests/dex_swap/scenarios/ -v
pytest tests/staking/scenarios/ -v
pytest tests/wallet_security/scenarios/ -v

# 运行 API 测试
pytest tests/api/scenarios/ -v

# 运行 RPC 测试
pytest tests/rpc/scenarios/ -v

# 运行 UI 测试（有头模式）
pytest tests/ui/scenarios/ --headed

# 运行对账测试
pytest tests/reconciliation/ -v

# 生成 Allure 报告
pytest --alluredir=allure-results
allure serve allure-results
```

## 📚 项目架构

### 四层架构设计

```
framework/          # 第 1 层：原子能力层（通用工具类）
├── core/          # 核心功能：日志、配置、数据工厂
├── api/           # API 客户端封装
├── web3/          # Web3 客户端封装（5 种客户端）
└── ui/            # UI 测试基础类

tests/             # 第 2-4 层：业务测试层
├── */apis/        # 第 2 层：单接口定义（只调用，不断言）
├── */fixtures/    # 第 3 层：场景组装（可断言）
└── */scenarios/   # 第 4 层：测试执行（验证结果）
```

### Web3 客户端架构

框架提供 5 种 Web3 客户端，适配不同测试场景：

| 客户端 | 用途 | 特点 |
|--------|------|------|
| **HardhatClient** | 合约部署和管理 | 编译、部署、获取 artifact |
| **Web3Client** | 通用 Web3 操作 | 交易、余额、合约调用 |
| **EthersClient** | Ethers.js 风格 | 类型安全、Provider/Signer |
| **ApeClient** | Ape 框架集成 | 快照、测试账户 |
| **BrownieClient** | Brownie 框架集成 | 项目管理、网络切换 |

**推荐使用**：
- 合约部署：`HardhatClient`
- 日常测试：`Web3Client`
- 类型安全：`EthersClient`

## 🧪 测试套件

### 1. 智能合约测试

#### NFT Mint 测试
```bash
pytest tests/nft_mint/scenarios/ -v
```

**测试场景**：
- 基础铸造（Mint NFT）
- 批量铸造
- 转账和授权
- 元数据查询
- 所有权验证
- 燃烧（Burn）

**合约**：`MockERC721.sol`

#### DEX Swap 测试
```bash
pytest tests/dex_swap/scenarios/ -v
```

**测试场景**：
- 添加流动性
- 移除流动性
- Token 交换
- 价格计算
- 滑点保护
- 手续费分配

**合约**：`MockDEX.sol`, `MockERC20.sol`

#### Staking 测试
```bash
pytest tests/staking/scenarios/ -v
```

**测试场景**：
- 质押代币
- 提取质押
- 奖励计算
- 奖励领取
- 锁定期验证
- 多用户质押

**合约**：`MockStaking.sol`, `MockERC20.sol`

#### Wallet Security 测试
```bash
pytest tests/wallet_security/scenarios/ -v
```

**测试场景**：
- EIP-2612 Permit 签名
- Gasless 授权
- 签名验证
- 重放攻击防护
- Personal Sign
- EIP-712 Typed Data

**合约**：`MockERC20Permit.sol`

### 2. API 测试

**架构**：
- `tests/api/apis/` - 单接口定义（user, wallet, transaction）
- `tests/api/fixtures/` - 场景组装
- `tests/api/scenarios/` - 测试执行

**示例**：
```python
def test_user_register_and_create_wallet(user_api, wallet_api, logged_in_user, validator):
    """场景：用户注册→登录→创建钱包→查询余额"""
    user_id = logged_in_user.get('user_id')

    response = wallet_api.create_wallet(user_id=user_id, wallet_type='ETH')
    assert validator.validate_status_code_in(response, [200, 201])
```

### 3. RPC 测试

**架构**：
- `tests/rpc/rpcs/` - RPC 接口定义（blockchain, contract）
- `tests/rpc/fixtures/` - 场景组装
- `tests/rpc/scenarios/` - 测试执行

**示例**：
```python
@retry_on_failure(max_retries=3, delay=1.0, backoff=2.0)
def test_query_latest_block(blockchain_rpc, rpc_validator):
    """查询最新区块（带重试）"""
    response = blockchain_rpc.get_block_number()
    assert rpc_validator.validate_rpc_response(response)
```

### 4. UI 测试

**架构**：
- `tests/ui/pages/` - Page Object（元素定位）
- `tests/ui/fixtures/` - 场景组装
- `tests/ui/scenarios/` - 测试执行

**示例**：
```python
def test_connect_wallet(connected_wallet):
    """场景：连接 MetaMask 钱包"""
    wallet_address = connected_wallet['wallet_address']
    assert wallet_address.startswith('0x')
```

## 🛠️ 核心工具类

### TestDataFactory - 测试数据生成

```python
from framework.core.test_data_factory import TestDataFactory

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

### WalletSigner - 钱包签名

```python
from framework.web3.wallet_signer import WalletSigner

# 创建钱包
signer = WalletSigner(private_key)

# Personal Sign
signature = signer.sign_message("Hello World")

# EIP-712 Typed Data
typed_data = {...}
signature = signer.sign_typed_data(typed_data)

# EIP-2612 Permit
permit_sig = signer.create_eip712_permit(
    token_name="MyToken",
    token_address="0x...",
    owner="0x...",
    spender="0x...",
    value=1000,
    nonce=0,
    deadline=9999999999,
    chain_id=31337
)
```

### RetryHelper - 重试机制

```python
from framework.core.retry_helper import retry_on_failure, RetryHelper

# 装饰器方式
@retry_on_failure(max_retries=3, delay=1.0, backoff=2.0)
def unstable_operation():
    pass

# 手动方式
helper = RetryHelper(max_retries=3, delay=1.0)
result = helper.retry(lambda: api.call())
```

### PollingHelper - 轮询机制

```python
from framework.core.polling_helper import PollingHelper

helper = PollingHelper()

# 轮询交易回执
receipt = helper.poll_transaction_receipt(
    get_receipt_func,
    tx_hash,
    timeout=120.0,
    interval=3.0
)
```

## 📂 项目结构

```
web3-auto-test/
├── contracts/                  # 智能合约
│   ├── MockERC20.sol          # ERC20 代币
│   ├── MockERC20Permit.sol    # 支持 Permit 的 ERC20
│   ├── MockERC721.sol         # ERC721 NFT
│   ├── MockDEX.sol            # DEX 交易所
│   └── MockStaking.sol        # 质押合约
│
├── framework/                  # 框架层（原子能力）
│   ├── core/                  # 核心功能
│   │   ├── logger.py          # 日志管理
│   │   ├── config.py          # 配置管理
│   │   ├── test_data_factory.py  # 测试数据工厂
│   │   ├── retry_helper.py    # 重试机制
│   │   └── polling_helper.py  # 轮询机制
│   ├── api/                   # API 客户端
│   │   ├── http_client.py     # HTTP 客户端
│   │   └── rpc_validator.py   # RPC 验证器
│   ├── web3/                  # Web3 客户端
│   │   ├── web3_client.py     # Web3.py 客户端
│   │   ├── hardhat_client.py  # Hardhat 客户端
│   │   ├── ethers_client.py   # Ethers.js 客户端
│   │   ├── ape_client.py      # Ape 客户端
│   │   ├── brownie_client.py  # Brownie 客户端
│   │   └── wallet_signer.py   # 钱包签名
│   └── ui/                    # UI 测试基础
│       └── base_page.py       # BasePage 类
│
├── tests/                     # 测试层
│   ├── nft_mint/             # NFT 铸造测试
│   │   ├── apis/             # NFT API 封装
│   │   ├── fixtures/         # 场景 fixtures
│   │   └── scenarios/        # 测试场景
│   ├── dex_swap/             # DEX 交换测试
│   ├── staking/              # 质押测试
│   ├── wallet_security/      # 钱包安全测试
│   ├── api/                  # API 测试
│   ├── rpc/                  # RPC 测试
│   ├── ui/                   # UI 测试
│   └── reconciliation/       # 对账测试
│
├── config/                    # 配置文件
│   ├── config.example.yaml   # 配置模板
│   └── local.yaml            # 本地配置
│
├── .claude/                   # Claude 技能
│   └── skills/
│       ├── generate-contract-test.skill.yaml  # 生成合约测试
│       ├── generate-api-test.skill.yaml       # 生成 API 测试
│       └── generate-ui-test.skill.yaml        # 生成 UI 测试
│
├── hardhat.config.js         # Hardhat 配置
├── package.json              # Node.js 依赖
├── requirements.txt          # Python 依赖
├── pytest.ini                # Pytest 配置
├── .env.example              # 环境变量模板
├── CLAUDE.md                 # Claude 指令文档
└── README.md                 # 项目文档
```

## 🎯 使用技能生成测试

框架提供了 3 个 Claude 技能，快速生成测试用例：

### 1. 生成智能合约测试

```bash
# 在 Claude Code 中使用
/generate-contract-test
```

**支持的合约类型**：
- NFT (ERC721)
- ERC20 Token
- DEX/AMM
- Staking
- Wallet Security

**生成内容**：
- 合约 API 封装（`tests/*/apis/`）
- 场景 fixtures（`tests/*/fixtures/`）
- 测试场景（`tests/*/scenarios/`）

### 2. 生成 API 测试

```bash
/generate-api-test
```

**支持的模块**：
- 用户管理
- 钱包操作
- 交易处理
- 合约交互

### 3. 生成 UI 测试

```bash
/generate-ui-test
```

**支持的场景**：
- 用户认证
- 钱包连接
- NFT 操作
- DeFi 操作

## 💡 最佳实践

### 1. 架构原则
- **framework/** 只提供原子能力，不包含业务逻辑
- **单接口**只负责调用，不包含断言
- **场景 fixtures** 可以包含断言和验证
- **测试用例**执行场景，验证结果

### 2. 测试数据
- 使用 `TestDataFactory` 生成唯一数据
- 避免硬编码测试数据
- 注意并发安全

### 3. 异步处理
- 使用 `RetryHelper` 处理不稳定操作
- 使用 `PollingHelper` 等待链上确认
- 合理设置超时时间

### 4. 报告增强
- 使用 `@allure.feature` 和 `@allure.story` 装饰器
- 使用 `with allure.step()` 记录步骤
- 失败时自动截图/录屏

### 5. 合约测试
- 启动 Hardhat 节点后再运行测试
- 使用 `HardhatClient` 部署合约
- 使用 `Web3Client` 进行交互
- 测试前编译合约：`npx hardhat compile`

## 🔧 常见问题

### 1. Hardhat 编译失败

**问题**：Node.js 版本不匹配

**解决**：
```bash
nvm use 22.13.0
npx hardhat compile
```

### 2. 测试连接失败

**问题**：Hardhat 节点未启动

**解决**：
```bash
# 启动节点
npx hardhat node
```
### 3. Nonce 冲突

**问题**：并发测试导致 nonce 冲突

**解决**：
- 使用 `pytest-xdist` 时设置 `-n 1`
- 或在 fixture 中使用不同账户

### 4. Gas 估算失败

**问题**：交易参数不正确

**解决**：
- 检查合约地址是否正确
- 检查函数参数是否匹配
- 查看 Hardhat 节点日志



### 项目文档
- `CLAUDE.md` - Claude 指令和快速模板
- `examples/` - 示例代码
- `tests/*/scenarios/` - 测试场景示例


### 开发流程
1. Fork 项目
2. 创建特性分支：`git checkout -b feature/xxx`
3. 提交代码：`git commit -m 'Add xxx'`
4. 推送分支：`git push origin feature/xxx`
5. 提交 Pull Request

### 代码规范
- 遵循 PEP 8 规范
- 使用类型注解
- 编写测试用例
- 更新文档


## 👨‍💻 作者

mayuming

---

**Happy Testing! 🚀**
