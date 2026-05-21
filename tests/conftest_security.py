"""
安全和性能测试 Fixtures
"""
import pytest
from framework.security import SlitherAnalyzer, MythrilScanner, GasAnalyzer, GasTracker


@pytest.fixture(scope="session")
def slither_analyzer():
    """Slither 静态分析器"""
    return SlitherAnalyzer()


@pytest.fixture(scope="session")
def mythril_scanner():
    """Mythril 安全扫描器"""
    return MythrilScanner()


@pytest.fixture(scope="function")
def gas_analyzer():
    """Gas 分析器（每个测试函数独立）"""
    analyzer = GasAnalyzer()
    yield analyzer
    # 测试结束后自动生成报告
    analyzer.save_report()


@pytest.fixture(scope="function")
def gas_tracker(gas_analyzer, web3_client):
    """Gas 追踪器"""
    return GasTracker(gas_analyzer, web3_client)
