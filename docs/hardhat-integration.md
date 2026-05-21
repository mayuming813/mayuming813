# Hardhat 集成说明

## 安装的工具

- **Hardhat 3.4.5**: 智能合约开发环境
- **@nomicfoundation/hardhat-ethers**: Ethers.js 集成
- **@openzeppelin/contracts**: OpenZeppelin 合约库
- **ethers 6.x**: 以太坊 JavaScript 库

## 合约说明

### MockERC20.sol
标准 ERC20 代币合约，用于测试：
- Mint/Burn 功能
- 转账功能
- 授权功能

### MockERC721.sol
NFT 合约，用于 NFT Mint 测试：
- 公开 Mint（需支付费用）
- Owner Mint（免费）
- 暂停/恢复功能
- 价格设置
- 提现功能

### SimpleDEX.sol
简单的 DEX 合约，用于 Swap 测试：
- 创建流动性池
- 添加/移除流动性
- Swap 交易（0.3% 手续费）
- 价格计算

### StakingPool.sol
质押挖矿合约，用于 Staking 测试：
- 质押代币
- 计算奖励
- 提取奖励
- 解押（带锁定期）

## 使用命令

```bash
# 编译合约
npm run compile

# 启动本地节点
npm run node

# 部署合约（Hardhat 网络）
npm run deploy

# 部署合约（本地节点）
npm run deploy:localhost

# 清理编译产物
npm run clean

# 运行 Hardhat 测试
npm run test:hardhat
```

## 报告目录

- `reports/gas/`: Gas 消耗报告
- `reports/security/`: 安全检测报告
- `reports/coverage/`: 代码覆盖率报告
- `reports/static-analysis/`: 静态代码分析报告

## 配置文件

`hardhat.config.js` 包含：
- Solidity 编译器版本：0.8.27
- 网络配置：hardhat, localhost
- 路径配置
- Gas Reporter 配置
- 合约大小检查配置

## 注意事项

1. 需要 Node.js 22.13.0 或更高版本
2. 项目使用 ESM 模块（`"type": "module"`）
3. 合约使用 OpenZeppelin 5.x（移除了 Counters）
4. Hardhat 3.x 网络配置需要指定 `type` 字段
