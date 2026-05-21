# 环境安装说明

## 问题说明

你的 macOS 系统 Python 受 PEP 668 保护，**不允许直接安装包到系统环境**。

这是为了保护系统 Python 不被破坏。

## 解决方案

**必须使用虚拟环境**（这是 Python 官方推荐的最佳实践）

### 快速开始

```bash
# 1. 创建虚拟环境（只需一次）
python3 -m venv venv

# 2. 激活虚拟环境（每次使用前）
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 安装 Playwright 浏览器
playwright install chromium

# 5. 运行测试
pytest tests/
```

### 为什么必须用虚拟环境？

1. **系统保护**：macOS 不允许修改系统 Python
2. **依赖隔离**：不同项目的依赖不会冲突
3. **版本管理**：可以为不同项目使用不同版本的包
4. **最佳实践**：Python 官方强烈推荐

### 虚拟环境很简单

虚拟环境只是一个文件夹（`venv/`），包含项目专用的 Python 和依赖包。

**优点**：
- ✓ 不影响系统 Python
- ✓ 项目依赖独立
- ✓ 可以随时删除重建
- ✓ 团队成员环境一致

**使用流程**：
```bash
# 每次打开新终端
cd /Users/mayuming/Desktop/web3-auto-test
source venv/bin/activate  # 激活虚拟环境

# 现在可以正常使用
pytest tests/
python xxx.py

# 退出虚拟环境（可选）
deactivate
```

### 一键脚本

已经创建好了 `check_env.sh`，会自动处理所有事情：

```bash
./check_env.sh
```

这个脚本会：
1. 创建虚拟环境
2. 激活虚拟环境
3. 安装所有依赖
4. 验证安装
5. 测试导入

### IDE 配置

**PyCharm**:
- Settings → Project → Python Interpreter
- 选择 `venv/bin/python`

**VS Code**:
- Cmd+Shift+P → Python: Select Interpreter
- 选择 `./venv/bin/python`

配置后，IDE 会自动使用虚拟环境，不需要手动激活。

### 常见问题

**Q: 虚拟环境会占用很多空间吗？**
A: 大约 200-300MB，可以随时删除重建。

**Q: 每次都要激活很麻烦？**
A: 在 `.zshrc` 添加别名：
```bash
alias web3test='cd /Users/mayuming/Desktop/web3-auto-test && source venv/bin/activate'
```
然后只需运行 `web3test` 即可。

**Q: 可以强制安装到系统吗？**
A: 可以用 `--break-system-packages`，但**强烈不推荐**，可能破坏系统。

### 总结

虚拟环境是 Python 开发的标准做法，不是额外负担，而是最佳实践。

**现在就开始**：
```bash
./check_env.sh
```

一切都会自动完成！