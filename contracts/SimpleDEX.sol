// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

/**
 * @title SimpleDEX
 * @dev 简单的 DEX 合约用于测试 Swap 功能
 */
contract SimpleDEX is Ownable, ReentrancyGuard {
    struct Pool {
        address tokenA;
        address tokenB;
        uint256 reserveA;
        uint256 reserveB;
        uint256 totalLiquidity;
    }

    mapping(bytes32 => Pool) public pools;
    mapping(bytes32 => mapping(address => uint256)) public liquidityBalances;

    event PoolCreated(bytes32 indexed poolId, address tokenA, address tokenB);
    event LiquidityAdded(bytes32 indexed poolId, address indexed provider, uint256 amountA, uint256 amountB, uint256 liquidity);
    event LiquidityRemoved(bytes32 indexed poolId, address indexed provider, uint256 amountA, uint256 amountB, uint256 liquidity);
    event Swapped(bytes32 indexed poolId, address indexed user, address tokenIn, uint256 amountIn, uint256 amountOut);

    constructor() Ownable(msg.sender) {}

    function getPoolId(address tokenA, address tokenB) public pure returns (bytes32) {
        (address token0, address token1) = tokenA < tokenB ? (tokenA, tokenB) : (tokenB, tokenA);
        return keccak256(abi.encodePacked(token0, token1));
    }

    function createPool(address tokenA, address tokenB) external onlyOwner {
        require(tokenA != tokenB, "Identical tokens");
        bytes32 poolId = getPoolId(tokenA, tokenB);
        require(pools[poolId].tokenA == address(0), "Pool already exists");

        (address token0, address token1) = tokenA < tokenB ? (tokenA, tokenB) : (tokenB, tokenA);
        pools[poolId] = Pool({
            tokenA: token0,
            tokenB: token1,
            reserveA: 0,
            reserveB: 0,
            totalLiquidity: 0
        });

        emit PoolCreated(poolId, token0, token1);
    }

    function addLiquidity(
        address tokenA,
        address tokenB,
        uint256 amountA,
        uint256 amountB
    ) external nonReentrant returns (uint256 liquidity) {
        bytes32 poolId = getPoolId(tokenA, tokenB);
        Pool storage pool = pools[poolId];
        require(pool.tokenA != address(0), "Pool does not exist");

        (uint256 amount0, uint256 amount1) = tokenA < tokenB ? (amountA, amountB) : (amountB, amountA);

        IERC20(pool.tokenA).transferFrom(msg.sender, address(this), amount0);
        IERC20(pool.tokenB).transferFrom(msg.sender, address(this), amount1);

        if (pool.totalLiquidity == 0) {
            liquidity = sqrt(amount0 * amount1);
        } else {
            liquidity = min(
                (amount0 * pool.totalLiquidity) / pool.reserveA,
                (amount1 * pool.totalLiquidity) / pool.reserveB
            );
        }

        require(liquidity > 0, "Insufficient liquidity minted");

        pool.reserveA += amount0;
        pool.reserveB += amount1;
        pool.totalLiquidity += liquidity;
        liquidityBalances[poolId][msg.sender] += liquidity;

        emit LiquidityAdded(poolId, msg.sender, amount0, amount1, liquidity);
    }

    function removeLiquidity(
        address tokenA,
        address tokenB,
        uint256 liquidity
    ) external nonReentrant returns (uint256 amountA, uint256 amountB) {
        bytes32 poolId = getPoolId(tokenA, tokenB);
        Pool storage pool = pools[poolId];
        require(pool.tokenA != address(0), "Pool does not exist");
        require(liquidityBalances[poolId][msg.sender] >= liquidity, "Insufficient liquidity");

        uint256 amount0 = (liquidity * pool.reserveA) / pool.totalLiquidity;
        uint256 amount1 = (liquidity * pool.reserveB) / pool.totalLiquidity;

        pool.reserveA -= amount0;
        pool.reserveB -= amount1;
        pool.totalLiquidity -= liquidity;
        liquidityBalances[poolId][msg.sender] -= liquidity;

        IERC20(pool.tokenA).transfer(msg.sender, amount0);
        IERC20(pool.tokenB).transfer(msg.sender, amount1);

        (amountA, amountB) = tokenA < tokenB ? (amount0, amount1) : (amount1, amount0);

        emit LiquidityRemoved(poolId, msg.sender, amountA, amountB, liquidity);
    }

    function swap(
        address tokenIn,
        address tokenOut,
        uint256 amountIn,
        uint256 minAmountOut
    ) external nonReentrant returns (uint256 amountOut) {
        bytes32 poolId = getPoolId(tokenIn, tokenOut);
        Pool storage pool = pools[poolId];
        require(pool.tokenA != address(0), "Pool does not exist");

        bool isTokenA = tokenIn < tokenOut;
        (uint256 reserveIn, uint256 reserveOut) = isTokenA
            ? (pool.reserveA, pool.reserveB)
            : (pool.reserveB, pool.reserveA);

        // 计算输出金额 (0.3% 手续费)
        uint256 amountInWithFee = amountIn * 997;
        amountOut = (amountInWithFee * reserveOut) / (reserveIn * 1000 + amountInWithFee);
        require(amountOut >= minAmountOut, "Slippage too high");

        IERC20(tokenIn).transferFrom(msg.sender, address(this), amountIn);
        IERC20(tokenOut).transfer(msg.sender, amountOut);

        if (isTokenA) {
            pool.reserveA += amountIn;
            pool.reserveB -= amountOut;
        } else {
            pool.reserveB += amountIn;
            pool.reserveA -= amountOut;
        }

        emit Swapped(poolId, msg.sender, tokenIn, amountIn, amountOut);
    }

    function getAmountOut(
        address tokenIn,
        address tokenOut,
        uint256 amountIn
    ) external view returns (uint256 amountOut) {
        bytes32 poolId = getPoolId(tokenIn, tokenOut);
        Pool storage pool = pools[poolId];
        require(pool.tokenA != address(0), "Pool does not exist");

        bool isTokenA = tokenIn < tokenOut;
        (uint256 reserveIn, uint256 reserveOut) = isTokenA
            ? (pool.reserveA, pool.reserveB)
            : (pool.reserveB, pool.reserveA);

        uint256 amountInWithFee = amountIn * 997;
        amountOut = (amountInWithFee * reserveOut) / (reserveIn * 1000 + amountInWithFee);
    }

    function sqrt(uint256 y) internal pure returns (uint256 z) {
        if (y > 3) {
            z = y;
            uint256 x = y / 2 + 1;
            while (x < z) {
                z = x;
                x = (y / x + x) / 2;
            }
        } else if (y != 0) {
            z = 1;
        }
    }

    function min(uint256 x, uint256 y) internal pure returns (uint256) {
        return x < y ? x : y;
    }
}
