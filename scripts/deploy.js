import hre from "hardhat";

async function main() {
  console.log("开始部署合约...");

  // 获取部署账户
  const [deployer] = await hre.ethers.getSigners();
  console.log("部署账户:", deployer.address);

  // 部署 MockERC20
  console.log("\n部署 MockERC20...");
  const MockERC20 = await hre.ethers.getContractFactory("MockERC20");
  const token = await MockERC20.deploy("Test Token", "TEST", 18);
  await token.waitForDeployment();
  console.log("MockERC20 部署地址:", await token.getAddress());

  // 部署 MockERC721
  console.log("\n部署 MockERC721...");
  const MockERC721 = await hre.ethers.getContractFactory("MockERC721");
  const nft = await MockERC721.deploy(
    "Test NFT",
    "TNFT",
    10000, // maxSupply
    hre.ethers.parseEther("0.01") // mintPrice
  );
  await nft.waitForDeployment();
  console.log("MockERC721 部署地址:", await nft.getAddress());

  // 部署 SimpleDEX
  console.log("\n部署 SimpleDEX...");
  const SimpleDEX = await hre.ethers.getContractFactory("SimpleDEX");
  const dex = await SimpleDEX.deploy();
  await dex.waitForDeployment();
  console.log("SimpleDEX 部署地址:", await dex.getAddress());

  // 部署第二个 ERC20 用于 DEX 测试
  console.log("\n部署第二个 MockERC20 (用于 DEX)...");
  const token2 = await MockERC20.deploy("Test Token 2", "TEST2", 18);
  await token2.waitForDeployment();
  console.log("MockERC20 (TEST2) 部署地址:", await token2.getAddress());

  // 部署 StakingPool
  console.log("\n部署 StakingPool...");
  const StakingPool = await hre.ethers.getContractFactory("StakingPool");
  const stakingPool = await StakingPool.deploy(
    await token.getAddress(), // stakingToken
    await token2.getAddress(), // rewardToken
    hre.ethers.parseEther("0.1"), // rewardRate: 0.1 tokens per second
    86400 // lockDuration: 1 day
  );
  await stakingPool.waitForDeployment();
  console.log("StakingPool 部署地址:", await stakingPool.getAddress());

  console.log("\n所有合约部署完成！");

  // 保存部署地址
  const deployments = {
    MockERC20: await token.getAddress(),
    MockERC20_2: await token2.getAddress(),
    MockERC721: await nft.getAddress(),
    SimpleDEX: await dex.getAddress(),
    StakingPool: await stakingPool.getAddress(),
    deployer: deployer.address,
    network: hre.network.name,
    timestamp: new Date().toISOString(),
  };

  console.log("\n部署信息:", JSON.stringify(deployments, null, 2));
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });