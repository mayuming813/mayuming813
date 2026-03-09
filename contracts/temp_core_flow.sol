// SPDX-License-Identifier: MIT
// 面向 Sepolia 测试网 + 高频单元测试的 Demo 合约。单次操作极省 gas，大量逻辑通过 view 暴露便于无 gas 测试。

pragma solidity ^0.8.20;

/**
 * @title SepoliaClaimFaucet
 * @notice 测试网水龙头：支持按总量/单人/冷却限制领取 ETH，便于高频测试并展示单元测试能力
 * @dev 设计要点：1) 单次 claim 仅 2～3 次存储写入，省 gas  2) 业务规则全部有 view 暴露，可纯 call 测试
 */
contract SepoliaClaimFaucet {
    // ------------------------- 状态（紧凑，省 gas）-------------------------
    address public owner;

    uint256 public claimAmount;      // 每次可领 wei
    uint256 public totalCap;         // 全局已领上限
    uint256 public perUserCap;       // 单人累计已领上限
    uint256 public cooldownSeconds;  // 两次领取最小间隔（秒）

    uint256 public totalClaimed;     // 当前已领总量
    mapping(address => uint256) public userClaimed;       // 用户累计已领
    mapping(address => uint256) public lastClaimAt;       // 上次领取时间戳

    // ------------------------- 事件 -------------------------
    event Claimed(address indexed user, uint256 amount, uint256 userTotal);
    event ParamsUpdated(uint256 claimAmount, uint256 totalCap, uint256 perUserCap, uint256 cooldownSeconds);
    event Withdrawn(address indexed to, uint256 amount);

    // ------------------------- 错误（便于单元测试断言）-------------------------
    error OnlyOwner();
    error NotEnoughBalance();
    error OverTotalCap();
    error OverUserCap();
    error CooldownActive(uint256 waitUntil);
    error ZeroClaimAmount();
    error ZeroAddress();

    modifier onlyOwner() {
        if (msg.sender != owner) revert OnlyOwner();
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    receive() external payable {}

    /**
     * 核心流程：用户领取一次
     * 单次仅 2～3 个 SSTORE + 1 次 transfer，适合高频测试
     */
    function claim() external {
        uint256 amount = _claimableAmount(msg.sender);
        if (amount == 0) {
            if (claimAmount == 0) revert ZeroClaimAmount();
            if (address(this).balance < claimAmount) revert NotEnoughBalance();
            if (totalClaimed + claimAmount > totalCap) revert OverTotalCap();
            if (userClaimed[msg.sender] + claimAmount > perUserCap) revert OverUserCap();
            (bool ok, uint256 waitUntil) = _canClaim(msg.sender);
            if (!ok) revert CooldownActive(waitUntil);
        }

        totalClaimed += amount;
        userClaimed[msg.sender] += amount;
        lastClaimAt[msg.sender] = block.timestamp;

        (bool sent,) = msg.sender.call{value: amount}("");
        if (!sent) revert NotEnoughBalance();

        emit Claimed(msg.sender, amount, userClaimed[msg.sender]);
    }

    /**
     * 管理员：更新领取参数（便于测试不同配置下的行为）
     */
    function setParams(
        uint256 _claimAmount,
        uint256 _totalCap,
        uint256 _perUserCap,
        uint256 _cooldownSeconds
    ) external onlyOwner {
        claimAmount = _claimAmount;
        totalCap = _totalCap;
        perUserCap = _perUserCap;
        cooldownSeconds = _cooldownSeconds;
        emit ParamsUpdated(_claimAmount, _totalCap, _perUserCap, _cooldownSeconds);
    }

    /**
     * 管理员：从合约提回 ETH（测试网回收或紧急）
     */
    function withdraw(uint256 amount) external onlyOwner {
        (bool sent,) = owner.call{value: amount}("");
        if (!sent) revert NotEnoughBalance();
        emit Withdrawn(owner, amount);
    }

    // ==================== 以下均为 view/pure，单元测试可大量 call 不耗 gas ====================

    /**
     * 是否可领（含冷却与上限检查）
     * @return can 是否可领
     * @return waitUntil 若因冷却不可领，则返回可领时间戳
     */
    function canClaim(address user) external view returns (bool can, uint256 waitUntil) {
        return _canClaim(user);
    }

    function _canClaim(address user) internal view returns (bool can, uint256 waitUntil) {
        if (claimAmount == 0) return (false, 0);
        if (address(this).balance < claimAmount) return (false, 0);
        if (totalClaimed + claimAmount > totalCap) return (false, 0);
        if (userClaimed[user] + claimAmount > perUserCap) return (false, 0);

        uint256 next = lastClaimAt[user] + cooldownSeconds;
        if (block.timestamp < next) return (false, next);
        return (true, 0);
    }

    /**
     * 当前用户本次可领数量（0 表示不可领）
     */
    function claimableAmount(address user) external view returns (uint256) {
        return _claimableAmount(user);
    }

    function _claimableAmount(address user) internal view returns (uint256) {
        (bool ok,) = _canClaim(user);
        if (!ok) return 0;
        uint256 capHeadroom = totalCap - totalClaimed;
        uint256 userHeadroom = perUserCap - userClaimed[user];
        uint256 byBalance = address(this).balance;
        uint256 amount = claimAmount;
        if (capHeadroom < amount) amount = capHeadroom;
        if (userHeadroom < amount) amount = userHeadroom;
        if (byBalance < amount) amount = byBalance;
        return amount;
    }

    /**
     * 全局参数（便于测试配置一致性）
     */
    function getParams() external view returns (
        uint256 _claimAmount,
        uint256 _totalCap,
        uint256 _perUserCap,
        uint256 _cooldownSeconds
    ) {
        return (claimAmount, totalCap, perUserCap, cooldownSeconds);
    }

    /**
     * 全局统计（便于测试总量与余额一致性）
     */
    function getStats() external view returns (
        uint256 _totalClaimed,
        uint256 _contractBalance
    ) {
        return (totalClaimed, address(this).balance);
    }

    /**
     * 用户维度统计（便于测试单人限额与冷却）
     */
    function getUserStats(address user) external view returns (
        uint256 _userClaimed,
        uint256 _lastClaimAt
    ) {
        return (userClaimed[user], lastClaimAt[user]);
    }
}
