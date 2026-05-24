# 🔒 安全和性能检查工具 - 快速参考

## 🚀 一键命令

```bash
# 运行所有快速检查（推荐）⭐
npm run check:all

# 单独运行
npm run check:slither    # 静态分析
npm run check:size       # 合约大小检查
npm run check:gas        # Gas 分析
```

## 📊 检查单个合约

```bash
# 静态分析
python3 -m framework.utils.security_check --contract contracts/SimpleDEX.sol --slither

# 合约大小
python3 -m framework.utils.contract_size

# Gas 分析
python3 -m framework.utils.gas_report --test tests/dex_swap/ --contract SimpleDEX
```

## 📁 报告位置

```
reports/
├── security/           # 安全报告
├── contract-size/      # 合约大小报告
└── gas/               # Gas 报告
```

## 📚 详细文档

- **快速开始** → [docs/QUICK_CHECK_GUIDE.md](docs/QUICK_CHECK_GUIDE.md)
- **详细文档** → [docs/SECURITY_TOOLS.md](docs/SECURITY_TOOLS.md)
- **完整总结** → [SECURITY_INTEGRATION_SUMMARY.md](SECURITY_INTEGRATION_SUMMARY.md)

## ✅ 测试结果

```
✅ 合约大小检查 - 5 个合约，0 个超限
✅ 静态分析 - 发现 8 个问题（3 个高危）
✅ 一键命令 - 所有功能正常
```

## 🔧 可选工具安装

```bash
# 安装 Slither（推荐）
pip install slither-analyzer

# 安装 Mythril（可选，较慢）
pip install mythril
```

## 💡 最佳实践

1. 每次提交前运行 `npm run check:all`
2. 发布前运行完整安全检查
3. 定期对比 Gas 消耗变化
4. 保持合约大小在 20KB 以下
