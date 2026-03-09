"""
本地钱包主流程 UI 自动化：直接打开并操作 MetaMask 扩展弹窗（谷歌浏览器插件），不依赖测试页。

一个浏览器、一个 popup 页，test_01 → test_02 → test_03 顺序执行，不重复开页。
依赖：.env 中 CONTRACT_ADDRESS、WALLET_EXTENSION_PATH（或默认路径）；建议先解锁并切到 Sepolia。
"""
import pytest
from playwright.sync_api import Page, expect

from config import settings
from tests.ui.locators import (
    POPUP_ANY_CONTINUE,
    POPUP_CONFIRM,
    RECEIVE,
    SEND,
    TESTID_AMOUNT_INPUT,
    TESTID_CONFIRM,
    TESTID_NEXT_BUTTON,
    TESTID_RECIPIENT_INPUT,
    TESTID_RECEIVE,
    TESTID_REVIEW_BUTTON,
    TESTID_SEND,
)


@pytest.mark.ui
class TestWalletMainFlow:
    """直接操作 MetaMask 扩展弹窗的主流程；三个用例共用同一浏览器、同一 popup 页，顺序执行。"""

    def test_01_open_metamask_popup_and_see_main_ui(
        self,
        shared_popup_page: Page,
    ) -> None:
        """
        步骤：共用页已在 fixture 中打开 popup；断言弹窗内主界面可见（发送/收款等）。
        """
        page = shared_popup_page
        page.wait_for_timeout(2000)
        # 断言：当前为扩展 popup 页
        assert "chrome-extension://" in page.url, "应在扩展页 URL"
        assert "home.html" in page.url, "应为扩展主界面 home.html"
        # 断言：主界面可见「发送」入口（优先 data-testid，再 role/文案回退）
        send_btn = page.get_by_test_id(TESTID_SEND).or_(
            page.get_by_role("button", name=SEND)
        ).or_(page.get_by_text(SEND)).first
        expect(send_btn).to_be_visible(timeout=12000)
        # 可选：主界面有「收款」则说明加载更完整（不强制）
        receive_btn = page.get_by_test_id(TESTID_RECEIVE).or_(
            page.get_by_role("button", name=RECEIVE)
        ).or_(page.get_by_text(RECEIVE)).first
        _ = receive_btn.is_visible(timeout=2000)

    def test_02_send_eth_from_popup_to_contract(
        self,
        shared_popup_page: Page,
        metamask_popup_url: str,
    ) -> None:
        """
        步骤：在同一 popup 页上先回到首页，再点击发送 → 填合约地址与金额 → 下一步/确认。
        """
        contract_address = getattr(settings, "contract_address", None) or ""
        if not contract_address:
            pytest.skip("未配置 CONTRACT_ADDRESS")

        popup = shared_popup_page
        # 回到 popup 主界面，保证从「发送」开始
        popup.goto(metamask_popup_url, wait_until="domcontentloaded")
        popup.wait_for_timeout(1500)
        assert "chrome-extension://" in popup.url and "home.html" in popup.url, "应在扩展主界面 home.html"

        send_btn = popup.get_by_test_id(TESTID_SEND).or_(
            popup.get_by_role("button", name=SEND)
        ).or_(popup.get_by_text(SEND)).first
        expect(send_btn).to_be_visible(timeout=8000)
        send_btn.click()
        popup.wait_for_timeout(1200)

        recipient_input = popup.get_by_test_id(TESTID_RECIPIENT_INPUT).or_(
            popup.locator("input[type=\"text\"], input:not([type=\"hidden\"])").first
        )
        recipient_input.wait_for(state="visible", timeout=8000)
        recipient_input.fill(contract_address)
        popup.wait_for_timeout(400)
        actual = recipient_input.input_value()
        assert contract_address in actual or contract_address.lower() in actual.lower(), "地址输入框应已填入合约地址"
        amount_input = popup.get_by_test_id(TESTID_AMOUNT_INPUT).or_(
            popup.locator("input[type=\"text\"], input:not([type=\"hidden\"])").nth(1)
        )
        if amount_input.count() > 0:
            amount_input.first.fill("0.001")
        popup.wait_for_timeout(400)

        next_btn = popup.get_by_test_id(TESTID_REVIEW_BUTTON).or_(
            popup.get_by_test_id(TESTID_NEXT_BUTTON)
        ).or_(popup.get_by_role("button", name=POPUP_ANY_CONTINUE)).first
        next_visible = next_btn.is_visible(timeout=3000)
        if next_visible:
            next_btn.click()
            popup.wait_for_timeout(800)
        confirm_btn = popup.get_by_test_id(TESTID_CONFIRM).or_(
            popup.get_by_role("button", name=POPUP_CONFIRM)
        ).first
        confirm_visible = confirm_btn.is_visible(timeout=5000)
        if confirm_visible:
            confirm_btn.click()
        popup.wait_for_timeout(1500)
        assert "chrome-extension://" in popup.url, "应保持在扩展页"
        assert next_visible or confirm_visible, "应出现「下一步」或「确认」按钮"

    def test_03_full_flow_popup_only(
        self,
        shared_popup_page: Page,
        metamask_popup_url: str,
    ) -> None:
        """
        步骤：在同一 popup 页上回到首页，再完整走一遍发送 → 填地址/金额 → 确认。
        """
        contract_address = getattr(settings, "contract_address", None) or ""
        if not contract_address:
            pytest.skip("未配置 CONTRACT_ADDRESS")

        page = shared_popup_page
        # 回到 popup 主界面
        page.goto(metamask_popup_url, wait_until="domcontentloaded")
        page.wait_for_timeout(1200)
        assert "home.html" in page.url, "应打开扩展主界面 home.html"

        send_btn = page.get_by_test_id(TESTID_SEND).or_(
            page.get_by_role("button", name=SEND)
        ).or_(page.get_by_text(SEND)).first
        expect(send_btn).to_be_visible(timeout=8000)
        send_btn.click()
        page.wait_for_timeout(1200)

        recipient_input = page.get_by_test_id(TESTID_RECIPIENT_INPUT).or_(
            page.locator("input[type=\"text\"], input:not([type=\"hidden\"])").first
        )
        recipient_input.wait_for(state="visible", timeout=8000)
        recipient_input.fill(contract_address)
        page.wait_for_timeout(300)
        actual_addr = recipient_input.input_value()
        assert contract_address in actual_addr or contract_address.lower() in actual_addr.lower(), "地址输入框应已填入合约地址"
        amount_input = page.get_by_test_id(TESTID_AMOUNT_INPUT).or_(
            page.locator("input[type=\"text\"], input:not([type=\"hidden\"])").nth(1)
        )
        if amount_input.count() > 0:
            amount_input.first.fill("0.001")
        page.wait_for_timeout(400)

        next_btn = page.get_by_test_id(TESTID_REVIEW_BUTTON).or_(
            page.get_by_test_id(TESTID_NEXT_BUTTON)
        ).or_(page.get_by_role("button", name=POPUP_ANY_CONTINUE)).first
        expect(next_btn).to_be_visible(timeout=5000)
        next_btn.click()
        page.wait_for_timeout(800)
        confirm_btn = page.get_by_test_id(TESTID_CONFIRM).or_(
            page.get_by_role("button", name=POPUP_CONFIRM)
        ).first
        expect(confirm_btn).to_be_visible(timeout=8000)
        confirm_btn.click()
        page.wait_for_timeout(1500)
        assert "chrome-extension://" in page.url, "确认后应仍在扩展内"
