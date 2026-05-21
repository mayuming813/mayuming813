# IDE 配置指南

## 问题原因

虚拟环境中的 pytest 已正常安装，但 IDE 仍然提示找不到模块，是因为：

**IDE 使用的 Python 解释器不是虚拟环境的 Python**

## 解决方案

### PyCharm 配置

1. 打开 PyCharm
2. 点击右下角的 Python 解释器（或 `File` → `Settings`）
3. 选择 `Project: web3-auto-test` → `Python Interpreter`
4. 点击齿轮图标 → `Add Interpreter` → `Add Local Interpreter`
5. 选择 `Existing environment`
6. 浏览到：`/Users/mayuming/Desktop/web3-auto-test/venv/bin/python`
7. 点击 `OK`

**或者快捷方式**：
- 点击右下角的 Python 版本
- 选择 `Add New Interpreter` → `Add Local Interpreter`
- 选择项目中的 `venv` 文件夹

### VS Code 配置

1. 打开 VS Code
2. 按 `Cmd + Shift + P`
3. 输入 `Python: Select Interpreter`
4. 选择 `./venv/bin/python` 或 `Enter interpreter path...`
5. 浏览到：`/Users/mayuming/Desktop/web3-auto-test/venv/bin/python`

**或者**：
- 点击左下角的 Python 版本
- 选择 `./venv/bin/python`

### 验证配置

配置完成后，在 IDE 中：

1. 打开任意 Python 文件
2. 查看右下角/左下角的 Python 版本
3. 应该显示类似：`Python 3.14.3 (venv)`

### 测试导入

在 IDE 中打开 Python 控制台或新建文件测试：

```python
import sys
print(sys.executable)
# 应该输出: /Users/mayuming/Desktop/web3-auto-test/venv/bin/python

import pytest
print(pytest.__version__)
# 应该输出: 8.4.2
```

## 常见问题

### Q1: 配置后仍然提示找不到模块

**解决**：
1. 重启 IDE
2. 清除 IDE 缓存：
   - PyCharm: `File` → `Invalidate Caches` → `Invalidate and Restart`
   - VS Code: 重新加载窗口 `Cmd + Shift + P` → `Reload Window`

### Q2: 看不到 venv 选项

**解决**：
1. 确保 venv 文件夹存在：`ls -la venv/`
2. 手动输入路径：`/Users/mayuming/Desktop/web3-auto-test/venv/bin/python`

### Q3: 多个 Python 版本混淆

**解决**：
1. 在 IDE 中明确选择虚拟环境的 Python
2. 不要选择系统 Python（`/usr/bin/python3` 或 `/opt/homebrew/bin/python3`）

## 终端 vs IDE

**终端**：
- 需要手动激活：`source venv/bin/activate`
- 激活后所有命令使用虚拟环境

**IDE**：
- 配置解释器后自动使用虚拟环境
- 不需要手动激活
- 运行/调试都会使用配置的解释器

## 快速验证

运行诊断脚本：

```bash
# 在终端（激活虚拟环境）
source venv/bin/activate
python diagnose.py

# 在 IDE 中直接运行 diagnose.py
```

两者输出应该一致，都显示：
- ✓ 在虚拟环境中
- ✓ Python 路径指向 venv
- ✓ 所有模块都能导入

## 推荐配置

### .vscode/settings.json

如果使用 VS Code，创建此文件：

```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
    "python.terminal.activateEnvironment": true,
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false,
    "python.testing.pytestArgs": [
        "tests"
    ]
}
```

### .idea 配置

PyCharm 会自动在 `.idea` 目录保存配置，无需手动创建。

## 总结

1. **虚拟环境已正常安装所有依赖** ✓
2. **需要配置 IDE 使用虚拟环境的 Python** ←  这是关键
3. **配置后重启 IDE**
4. **运行 diagnose.py 验证**

配置完成后，IDE 中的导入错误提示会消失。
