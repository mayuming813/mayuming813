#!/bin/bash

# 安全和性能工具验证脚本

echo "=================================="
echo "安全和性能工具验证"
echo "=================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试计数
PASSED=0
FAILED=0

# 测试函数
test_command() {
    local name=$1
    local cmd=$2

    echo -n "测试 $name ... "

    if eval "$cmd" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ 通过${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗ 失败${NC}"
        ((FAILED++))
        return 1
    fi
}

# 1. 检查 Python 环境
echo "1. 检查 Python 环境"
test_command "Python3" "which python3"
echo ""

# 2. 检查脚本可执行性
echo "2. 检查脚本可执行性"
test_command "security_check.py" "python3 -m framework.utils.security_check --help"
test_command "contract_size.py" "python3 -m framework.utils.contract_size --help"
test_command "gas_report.py" "python3 -m framework.utils.gas_report --help"
echo ""

# 3. 检查合约文件
echo "3. 检查合约文件"
test_command "contracts 目录" "test -d contracts"
test_command "artifacts 目录" "test -d artifacts/contracts/contracts"
echo ""

# 4. 运行实际检查
echo "4. 运行实际检查"

echo -n "运行合约大小检查 ... "
if python3 -m framework.utils.contract_size --artifacts artifacts/contracts/contracts > /tmp/size_check.log 2>&1; then
    echo -e "${GREEN}✓ 通过${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ 失败${NC}"
    ((FAILED++))
fi

echo -n "运行静态分析 ... "
if python3 -m framework.utils.security_check --contract contracts/MockERC20.sol --slither > /tmp/security_check.log 2>&1; then
    echo -e "${GREEN}✓ 通过${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ 失败${NC}"
    ((FAILED++))
fi

echo ""

# 5. 检查报告生成
echo "5. 检查报告生成"
test_command "security 报告" "test -f reports/security/basic-analysis-MockERC20.json"
test_command "contract-size 报告" "test -f reports/contract-size/contract-size-report.txt"
echo ""

# 6. 检查 npm scripts
echo "6. 检查 npm scripts"
test_command "check:slither" "npm run check:slither --silent"
test_command "check:size" "npm run check:size --silent"
echo ""

# 总结
echo "=================================="
echo "验证总结"
echo "=================================="
echo -e "通过: ${GREEN}$PASSED${NC}"
echo -e "失败: ${RED}$FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ 所有测试通过！${NC}"
    echo ""
    echo "下一步："
    echo "  1. 运行完整检查: npm run check:all"
    echo "  2. 查看报告: cat reports/contract-size/contract-size-report.txt"
    echo "  3. 阅读文档: docs/QUICK_CHECK_GUIDE.md"
    exit 0
else
    echo -e "${RED}✗ 部分测试失败${NC}"
    echo ""
    echo "请检查："
    echo "  1. Python3 是否正确安装"
    echo "  2. 合约是否已编译"
    echo "  3. 查看日志: /tmp/size_check.log, /tmp/security_check.log"
    exit 1
fi
