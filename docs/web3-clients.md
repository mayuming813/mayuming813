# Web3 调用封装说明

本模块提供了多种 Web3 调用方式的封装，适用于不同的测试场景。

## 模块列表

### 1. Web3Client - Web3.py 直接调用

最底层的封装，直接使用 Web3.py API。

**适用场景：**
- 需要完全控制 Web3 调用细节
- 底层区块链交互
- 自定义交易构建

**示例：**
```python
from framework.web3 import Web3Client

client = Web3Client("http://127.0.0.1:8545")

# 获取区块号
block_number = client.get_block_number()

# 获取余额
balance = client.get_balance("0x...")

# 发送交易
from eth_account import Account
account = Account.from_key("0x...")
tx_hash = client.send_transaction(account, "0x...", value=client.to_wei(1, 'ether'))

# 加载合约
contract = client.load_contract("0x...", abi)
result = client.call_contract_function(contract, "balanceOf", "0x...")
```

### 2. EthersClient - Ethers.js 风格

模仿 Ethers.js 的 API 风格，适合熟悉 JavaScript 的开发者。

**适用场景：**
- 从 JavaScript 迁移的测试
- 需要 Ethers.js 风格的 API
- 合约交互

**示例：**
```python
from framework.web3 import EthersClient

client = EthersClient("http://127.0.0.1:8545")

# 获取签名者
signer = client.get_signer("0x...")

# 获取合约
contract = client.get_contract("0x...", abi, signer)

# 调用只读方法
balance = await client.call(contract, "balanceOf", "0x...")

# 发送交易
receipt = await client.send_transaction(contract, "transfer", "0x...", 1000)

# 解析单位
amount = client.parse_ether("1.5")
formatted = client.format_ether(amount)
```

### 3. HardhatClient - Hardhat 集成

专门用于 Hardhat 环境的合约部署和测试。

**适用场景：**
- 合约编译和部署
- 单元测试
- 本地开发环境

**示例：**
```python
from framework.web3 import HardhatClient

client = HardhatClient()

# 编译合约
client.compile()

# 部署合约
address = client.deploy_contract("MockERC20", ["Test Token", "TEST", 18])

# 获取合约实例
contract = client.get_contract("MockERC20", address)

# 获取签名者
signers = client.get_signers(10)

# 运行脚本
client.run_script("scripts/deploy.js")
```

### 4. RPCClient - JSON-RPC 调用

直接的 JSON-RPC 调用，适合测试 RPC 接口。

**适用场景：**
- RPC 接口测试
- 批量调用
- 调试和追踪

**示例：**
```python
from framework.web3 import RPCClient

client = RPCClient("http://127.0.0.1:8545")

# 单个调用
response = client.eth_block_number()
block_number = response['result']

# 批量调用
calls = [
    {"method": "eth_blockNumber"},
    {"method": "eth_gasPrice"},
    {"method": "net_version"}
]
results = client.batch_call(calls)

# Hardhat 特定方法
client.hardhat_impersonate_account("0x...")
client.hardhat_set_balance("0x...", "0x56BC75E2D63100000")  # 100 ETH
client.evm_increase_time(86400)  # 增加 1 天
```

### 5. WalletSigner - 钱包签名

钱包签名和验证功能。

**适用场景：**
- 消息签名测试
- EIP-712 签名
- 签名验证
- 钱包安全测试

**示例：**
```python
from framework.web3 import WalletSigner

# 创建钱包
wallet = WalletSigner.create_random_wallet()
print(wallet.address)
print(wallet.private_key)

# 从私钥创建
wallet = WalletSigner("0x...")

# 签名消息
result = wallet.sign_message("Hello World")
signature = result['signature']

# 验证签名
is_valid = WalletSigner.verify_signature("Hello World", signature, wallet.address)

# EIP-712 签名
typed_data = {...}
result = wallet.sign_typed_data(typed_data)

# EIP-2612 Permit
permit = wallet.create_eip712_permit(
    token_name="USDC",
    token_address="0x...",
    owner=wallet.address,
    spender="0x...",
    value=1000000,
    nonce=0,
    deadline=1234567890
)

# 从助记词创建
wallet = WalletSigner.from_mnemonic(
    "test test test test test test test test test test test junk",
    account_path="m/44'/60'/0'/0/0"
)
```

## 使用建议

1. **API 测试**: 使用 `Web3Client` 或 `EthersClient`
2. **RPC 测试**: 使用 `RPCClient`
3. **单元测试**: 使用 `HardhatClient`
4. **签名测试**: 使用 `WalletSigner`
5. **UI 测试**: 结合 `Web3Client` 和 `WalletSigner`

## 注意事项

- 所有客户端都支持 Hardhat 本地网络
- `EthersClient` 的异步方法需要在 async 函数中调用
- `HardhatClient` 需要 Node.js 环境
- `WalletSigner` 的私钥应妥善保管，不要提交到代码库
