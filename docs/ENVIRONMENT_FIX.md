# 环境问题解决方案

## 问题原因

你遇到的 `ModuleNotFoundError` 是因为：
1. **没有激活虚拟环境**：直接使用系统 Python，依赖包安装在虚拟环境中
2. **web3.py 版本兼容性**：新版本 web3.py (v7.x) 的中间件导入方式改变了

## 已修复的问题

### 1. Web3.py 中间件兼容性

**问题**：
```python
from web3.middleware import geth_poa_middleware  # v7.x 中不存在
```

**修复**：
```python
try:
    # web3.py v6.x
    from web3.middleware import geth_poa_middleware
except ImportError:
    # web3.py v7.x
    from web3.middleware import ExtraDataToPOAMiddleware as geth_poa_middleware
```

### 2. Web3Manager 延迟初始化

**问题**：模块导入时立即尝试连接 RPC，导致无 RPC 服务时无法导入

**修复**：改为延迟初始化，只有在实际使用时才连接 RPC

## 使用方法

### 方式1：使用检查脚本（推荐）

```bash
# 运行环境检查和修复脚本
./check_env.sh
```

这个脚本会：
- ✓ 检查 Python 版本
- ✓ 创建/检查虚拟环境
- ✓ 激活虚拟环境
- ✓ 升级 pip
- ✓ 安装所有依赖
- ✓ 安装 Playwright 浏览器
- ✓ 创建必要的目录
- ✓ 检查配置文件
- ✓ 测试模块导入
- ✓ 验证 pytest

### 方式2：手动操作

```bash
# 1. 激活虚拟环境（重要！）
source venv/bin/activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 安装 Playwright 浏览器
playwright install chromium

# 4. 测试导入
./test_imports.sh
```

### 方式3：IDE 配置

如果使用 PyCharm 或 VS Code：

**PyCharm**:
1. File → Settings → Project → Python Interpreter
2. 选择 `venv/bin/python`

**VS Code**:
1. Cmd+Shift+P → Python: Select Interpreter
2. 选择 `./venv/bin/python`

## 验证环境

运行测试导入脚本：

```bash
./test_imports.sh
```

应该看到：
```
=== 测试所有模块导入 ===

1. 测试核心模块...
   ✓ framework.core.config
   ✓ framework.core.logger
   ✓ framework.core.web3_manager

2. 测试 fixtures...
   ✓ framework.fixtures.common
   ✓ framework.fixtures.contracts
   ✓ framework.fixtures.ui

...

=== 所有模块导入测试通过 ✓ ===
```

## 运行测试

```bash
# 确保激活虚拟环境
source venv/bin/activate

# 运行示例测试
pytest tests/examples/test_data_driven.py -v

# 运行所有测试
pytest tests/ -v

# 查看测试用例列表
pytest --collect-only
```

## 常见问题

### Q1: 提示 "command not found: pytest"

**原因**：没有激活虚拟环境

**解决**：
```bash
source venv/bin/activate
```

### Q2: 提示 "ModuleNotFoundError: No module named 'xxx'"

**原因**：依赖包没有安装或没有激活虚拟环境

**解决**：
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Q3: 提示 "ConnectionError: 无法连接到 RPC"

**原因**：测试需要连接区块链节点，但节点未启动

**解决**：
- 启动本地测试网络（如 Ganache）
- 或修改 `.env` 中的 RPC URL 为可用的节点

### Q4: IDE 中仍然提示导入错误

**原因**：IDE 使用的 Python 解释器不是虚拟环境

**解决**：
- PyCharm: Settings → Project → Python Interpreter → 选择 `venv/bin/python`
- VS Code: Cmd+Shift+P → Python: Select Interpreter → 选择 `./venv/bin/python`

## 每次使用前

**重要**：每次打开新终端都需要激活虚拟环境！

```bash
cd /Users/mayuming/Desktop/web3-auto-test
source venv/bin/activate
```

或者在 `.bashrc` / `.zshrc` 中添加别名：

```bash
alias web3test='cd /Users/mayuming/Desktop/web3-auto-test && source venv/bin/activate'
```

然后只需运行：
```bash
web3test
```

## 脚本说明

### check_env.sh
完整的环境检查和修复脚本，包括：
- 虚拟环境创建
- 依赖安装
- 浏览器安装
- 目录创建
- 配置检查
- 模块导入测试

### test_imports.sh
快速测试所有模块是否可以正常导入

### setup.sh
初始化脚本（功能类似 check_env.sh）

## 依赖版本

当前使用的关键依赖版本：
- Python: 3.14.3
- pytest: 8.4.2
- web3.py: 7.14.1
- playwright: 1.40+
- allure-pytest: 2.15.3

## 下一步

环境配置完成后：
1. 编辑 `.env` 文件填入实际配置
2. 将合约 ABI 放入 `artifacts/` 目录
3. 运行测试：`pytest tests/`
4. 生成报告：`allure serve allure-results`
