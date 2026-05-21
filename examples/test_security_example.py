"""
安全测试示例 - 静态分析和安全扫描
"""
import pytest
import allure


@allure.feature("Security")
@allure.story("Static Analysis")
class TestStaticAnalysis:
    """静态分析测试"""

    def test_slither_analysis(self, slither_analyzer):
        """测试：运行 Slither 静态分析"""
        with allure.step("运行静态分析"):
            result = slither_analyzer.analyze()

        with allure.step("检查分析结果"):
            assert result.get("success", True), f"分析失败: {result.get('error')}"

        with allure.step("检查高危漏洞"):
            high_severity = slither_analyzer.get_high_severity_issues(result)
            assert len(high_severity) == 0, f"发现 {len(high_severity)} 个高危漏洞"

        with allure.step("生成报告"):
            report = slither_analyzer.generate_report(result)
            allure.attach(report, name="Static Analysis Report", attachment_type=allure.attachment_type.TEXT)


@allure.feature("Security")
@allure.story("Security Scan")
class TestSecurityScan:
    """安全扫描测试"""

    @pytest.mark.slow
    def test_mythril_scan_nft_contract(self, mythril_scanner):
        """测试：扫描 NFT 合约"""
        contract_path = "contracts/NFTMint.sol"

        with allure.step(f"扫描合约: {contract_path}"):
            result = mythril_scanner.scan(contract_path, max_depth=12, execution_timeout=120)

        with allure.step("检查扫描结果"):
            if not result.get("success", True):
                pytest.skip(f"扫描失败: {result.get('error')}")

        with allure.step("检查严重问题"):
            critical_issues = mythril_scanner.get_critical_issues(result)
            assert len(critical_issues) == 0, f"发现 {len(critical_issues)} 个严重安全问题"

        with allure.step("生成报告"):
            report = mythril_scanner.generate_report(result)
            allure.attach(report, name="Security Scan Report", attachment_type=allure.attachment_type.TEXT)


@allure.feature("Performance")
@allure.story("Gas Analysis")
class TestGasAnalysis:
    """Gas 分析测试"""

    def test_gas_tracking(self, gas_analyzer, nft_contract_api, test_accounts):
        """测试：追踪 NFT 铸造 Gas 消耗"""
        owner = test_accounts[0]
        recipient = test_accounts[1]

        with allure.step("铸造 NFT 并记录 Gas"):
            for i in range(3):
                tx_hash = nft_contract_api.mint(
                    recipient,
                    f"ipfs://test-token-{i}",
                    owner
                )
                receipt = nft_contract_api.client.w3.eth.get_transaction_receipt(tx_hash)
                gas_analyzer.record_transaction("mint", receipt["gasUsed"], tx_hash)

        with allure.step("检查 Gas 消耗"):
            avg_gas = gas_analyzer.get_average_gas("mint")
            assert avg_gas is not None, "未记录到 Gas 数据"
            assert avg_gas < 200000, f"Gas 消耗过高: {avg_gas}"

        with allure.step("生成 Gas 报告"):
            report = gas_analyzer.generate_report("NFTMint")
            allure.attach(report, name="Gas Report", attachment_type=allure.attachment_type.TEXT)

    def test_gas_comparison(self, gas_analyzer, nft_contract_api, test_accounts):
        """测试：对比不同操作的 Gas 消耗"""
        owner = test_accounts[0]
        recipient = test_accounts[1]

        with allure.step("测试 mint 操作"):
            tx_hash = nft_contract_api.mint(recipient, "ipfs://token-1", owner)
            receipt = nft_contract_api.client.w3.eth.get_transaction_receipt(tx_hash)
            gas_analyzer.record_transaction("mint", receipt["gasUsed"], tx_hash)

        with allure.step("测试 transfer 操作"):
            # 先铸造一个 NFT
            tx_hash = nft_contract_api.mint(owner, "ipfs://token-2", owner)
            nft_contract_api.client.w3.eth.wait_for_transaction_receipt(tx_hash)

            # 转账
            tx_hash = nft_contract_api.transfer_from(owner, recipient, 1, owner)
            receipt = nft_contract_api.client.w3.eth.get_transaction_receipt(tx_hash)
            gas_analyzer.record_transaction("transferFrom", receipt["gasUsed"], tx_hash)

        with allure.step("对比 Gas 消耗"):
            mint_gas = gas_analyzer.get_average_gas("mint")
            transfer_gas = gas_analyzer.get_average_gas("transferFrom")

            assert mint_gas > transfer_gas, "mint 应该比 transfer 消耗更多 Gas"

            report = gas_analyzer.generate_report("NFTMint")
            allure.attach(report, name="Gas Comparison Report", attachment_type=allure.attachment_type.TEXT)
