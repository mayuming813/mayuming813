import "@nomicfoundation/hardhat-ethers";

/** @type import('hardhat/config').HardhatUserConfig */
export default {
  solidity: {
    version: "0.8.27",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200,
      },
    },
  },

  networks: {
    hardhat: {
      type: "edr-simulated",
      chainId: 31337,
    },
    localhost: {
      type: "http",
      url: "http://127.0.0.1:8545",
      chainId: 31337,
    },
  },

  paths: {
    sources: "./contracts",
    tests: "./tests/unit/scenarios",
    cache: "./artifacts/cache",
    artifacts: "./artifacts/contracts",
  },

  mocha: {
    timeout: 120000,
  },

  // Gas Reporter 配置（需要单独安装插件时启用）
  gasReporter: {
    enabled: process.env.REPORT_GAS === "true",
    currency: "USD",
    outputFile: "reports/gas-report.txt",
    noColors: true,
    coinmarketcap: process.env.COINMARKETCAP_API_KEY || "",
  },

  // 合约大小检查
  contractSizer: {
    alphaSort: true,
    disambiguatePaths: false,
    runOnCompile: true,
    strict: true,
    outputFile: "reports/contract-size-report.txt",
  },
};
