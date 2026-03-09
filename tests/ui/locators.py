"""
MetaMask 界面元素定位：优先使用官方 data-testid，无则回退到 role/文案。

参考：MetaMask 官方仓库中的 data-testid（如 recipient-address-input、review-button、
     token-asset-${chainId}-${symbol}、page-container 等），不同版本可能略有差异。
"""
import re

# =============================================================================
# 官方 data-testid（MetaMask 扩展源码中用于 E2E/组件测试）
# =============================================================================
# 主界面 / 首页
TESTID_PAGE_CONTAINER = "page-container"
TESTID_HOME = "home"

# 首页四大操作（扩展内可能为 button 或可点击区域，以实际 DOM 为准）
TESTID_SEND = "send-token-button"  # 或 home__send-button 等，版本差异大时用回退
TESTID_RECEIVE = "receive-token-button"
TESTID_BUY = "buy-button"
TESTID_SWAP = "swap-button"

# 发送流程（官方 E2E 使用）
TESTID_RECIPIENT_INPUT = "recipient-address-input"
TESTID_AMOUNT_INPUT = "amount-input"
TESTID_REVIEW_BUTTON = "review-button"  # 发送流程中的「下一步/Review」
TESTID_CONFIRM_BUTTON = "confirm-footer-button"  # 确认页底部确认
TESTID_NEXT_BUTTON = "page-container__next-button"  # 部分确认页「下一步」

# 确认/弹窗通用（PageContainerFooter 等）
TESTID_CONFIRM = "confirm-footer-button"
TESTID_REJECT = "reject-footer-button"

# 代币选择（动态：token-asset-${chainId}-${symbol}）
def token_asset_testid(chain_id: int, symbol: str) -> str:
    """e.g. token-asset-11155111-SepoliaETH"""
    return f"token-asset-{chain_id}-{symbol}"

# =============================================================================
# 回退用：按 role/文案匹配（无 data-testid 或旧版本时）
# =============================================================================
ACCOUNT_DROPDOWN = re.compile(r"Account\s*1|账户\s*1", re.I)
BUY = re.compile(r"买入|Buy", re.I)
SWAP = re.compile(r"兑换|Swap", re.I)
SEND = re.compile(r"发送|Send", re.I)
RECEIVE = re.compile(r"收款|Receive", re.I)
TAB_TOKENS = re.compile(r"代币|Tokens", re.I)
TAB_ACTIVITY = re.compile(r"活动|Activity", re.I)
NETWORK_SEPOLIA = re.compile(r"Sepolia", re.I)
POPUP_NEXT = re.compile(r"下一步|Next", re.I)
POPUP_CONNECT = re.compile(r"连接|Connect", re.I)
POPUP_CONFIRM = re.compile(r"确认|Confirm|批准|Approve", re.I)
POPUP_REJECT = re.compile(r"拒绝|Reject", re.I)
POPUP_ANY_CONTINUE = re.compile(r"下一步|Next|连接|Connect|确认|Confirm|批准|Approve", re.I)
SEND_INPUT_ADDRESS = re.compile(r"收件人|Recipient|地址|Address|0x", re.I)
SEND_INPUT_AMOUNT = re.compile(r"金额|Amount|数量", re.I)
