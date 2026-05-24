#!/bin/bash
# 快速启动脚本

echo "=== Web3 自动化测试环境初始化 ==="

# 检查 Python 版本
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python 版本: $python_version"

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "安装 Python 依赖..."
pip install -r requirements.txt

# 安装 Playwright 浏览器
echo "安装 Playwright 浏览器..."
playwright install chromium

# 创建必要的目录
echo "创建目录结构..."
mkdir -p logs
mkdir -p screenshots
mkdir -p videos
mkdir -p traces
mkdir -p allure-results
mkdir -p allure-report
mkdir -p data/api
mkdir -p data/unit
mkdir -p data/integration
mkdir -p data/ui

# 检查环境变量文件
if [ ! -f ".env" ]; then
    echo "警告: .env 文件不存在"
    echo "请复制 .env.example 为 .env 并填入实际配置"
    cp .env.example .env
    echo "已创建 .env 文件，请编辑填入实际值"
fi

# 检查配置文件
if [ ! -f "config/local.yaml" ]; then
    echo "提示: config/local.yaml 不存在（可选）"
    echo "非敏感配置可以在此文件中覆盖 config.example.yaml"
fi

echo ""
echo "=== 初始化完成 ==="
echo ""
echo "下一步操作:"
echo "1. 编辑 .env 填入敏感配置（私钥、密码等）"
echo "2. 将合约 ABI 放入 artifacts/ 目录"
echo "3. 在 .env 中配置合约地址"
echo "4. 运行测试: pytest tests/"
echo "5. 生成报告: allure serve allure-results"
echo ""
echo "数据驱动测试:"
echo "- 测试数据放在 data/ 目录"
echo "- 使用 @parametrize_data 装饰器快速引用"
echo "- 参考 tests/examples/test_data_driven.py"
echo ""