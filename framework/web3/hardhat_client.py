#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : hardhat_client.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : Hardhat 合约交互封装
"""

import json
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List
from web3 import Web3
from eth_account import Account
from framework.core.logger import logger
from framework.web3.web3_client import Web3Client


class HardhatClient:
    """Hardhat 合约交互封装"""

    def __init__(self, project_root: Optional[str] = None):
        """
        初始化 Hardhat 客户端

        Args:
            project_root: Hardhat 项目根目录
        """
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.artifacts_dir = self.project_root / "artifacts" / "contracts"
        self.deployments_file = self.project_root / "deployments.json"

        # 默认连接到 Hardhat 本地网络
        self.web3_client = Web3Client("http://127.0.0.1:8545")

        # Enable HD wallet features for Account.from_mnemonic
        Account.enable_unaudited_hdwallet_features()

        logger.info(f"Hardhat 客户端已初始化: {self.project_root}")

    def compile(self) -> bool:
        """
        编译合约

        Returns:
            是否成功
        """
        try:
            # 使用 shell=True 来确保使用正确的 Node 版本
            result = subprocess.run(
                "source ~/.nvm/nvm.sh && nvm use 22.13.0 && npx hardhat compile",
                cwd=self.project_root,
                capture_output=True,
                text=True,
                shell=True,
                executable="/bin/bash"
            )
            if result.returncode != 0:
                logger.error(f"合约编译失败: {result.stderr}")
                return False
            logger.info("合约编译成功")
            logger.debug(result.stdout)
            return True
        except Exception as e:
            logger.error(f"合约编译失败: {e}")
            return False

    def deploy_contract(
        self,
        contract_name: str,
        constructor_args: Optional[List] = None,
        deployer: Optional[Account] = None
    ) -> Optional[str]:
        """
        部署合约

        Args:
            contract_name: 合约名称
            constructor_args: 构造函数参数
            deployer: 部署账户

        Returns:
            合约地址
        """
        # 加载合约 ABI 和 Bytecode
        abi, bytecode = self.load_contract_artifact(contract_name)
        if not abi or not bytecode:
            logger.error(f"无法加载合约 {contract_name} 的 artifact")
            return None

        # 创建合约实例
        contract = self.web3_client.w3.eth.contract(abi=abi, bytecode=bytecode)

        # 构建部署交易
        if not deployer:
            # 使用 Hardhat 默认账户
            deployer = self.get_default_signer()

        constructor = contract.constructor(*(constructor_args or []))
        tx = constructor.build_transaction({
            'from': deployer.address,
            'nonce': self.web3_client.w3.eth.get_transaction_count(deployer.address),
            'gas': 5000000,
            'gasPrice': self.web3_client.w3.eth.gas_price,
        })

        # 签名并发送交易
        signed_tx = self.web3_client.w3.eth.account.sign_transaction(tx, deployer.key)
        tx_hash = self.web3_client.w3.eth.send_raw_transaction(signed_tx.raw_transaction)

        # 等待交易确认
        receipt = self.web3_client.w3.eth.wait_for_transaction_receipt(tx_hash)
        contract_address = receipt['contractAddress']

        logger.info(f"合约 {contract_name} 已部署: {contract_address}")

        # 保存部署信息
        self.save_deployment(contract_name, contract_address, tx_hash.hex())

        return contract_address

    def load_contract_artifact(self, contract_name: str) -> tuple[Optional[List], Optional[str]]:
        """
        加载合约 artifact

        Args:
            contract_name: 合约名称

        Returns:
            (ABI, Bytecode)
        """
        # Try the new Hardhat 3.x structure first: artifacts/contracts/contracts/{name}.sol/{name}.json
        artifact_file = self.artifacts_dir / "contracts" / f"{contract_name}.sol" / f"{contract_name}.json"

        # Fallback to old structure: artifacts/contracts/{name}.sol/{name}.json
        if not artifact_file.exists():
            artifact_file = self.artifacts_dir / f"{contract_name}.sol" / f"{contract_name}.json"

        if not artifact_file.exists():
            logger.error(f"Artifact 文件不存在: {artifact_file}")
            return None, None

        with open(artifact_file, 'r') as f:
            artifact = json.load(f)

        return artifact.get('abi'), artifact.get('bytecode')

    def get_contract(self, contract_name: str, address: Optional[str] = None) -> Any:
        """
        获取合约实例

        Args:
            contract_name: 合约名称
            address: 合约地址（如果不提供，从部署记录中读取）

        Returns:
            合约实例
        """
        if not address:
            address = self.get_deployment_address(contract_name)
            if not address:
                logger.error(f"未找到合约 {contract_name} 的部署地址")
                return None

        abi, _ = self.load_contract_artifact(contract_name)
        if not abi:
            return None

        return self.web3_client.load_contract(address, abi)

    def get_default_signer(self) -> Account:
        """
        获取 Hardhat 默认签名者（第一个账户）

        Returns:
            Account 对象
        """
        # Hardhat 默认助记词
        mnemonic = "test test test test test test test test test test test junk"
        account = Account.from_mnemonic(mnemonic, account_path="m/44'/60'/0'/0/0")
        return account

    def get_signers(self, count: int = 10) -> List[Account]:
        """
        获取多个签名者

        Args:
            count: 账户数量

        Returns:
            Account 列表
        """
        mnemonic = "test test test test test test test test test test test junk"
        signers = []
        for i in range(count):
            account = Account.from_mnemonic(mnemonic, account_path=f"m/44'/60'/0'/0/{i}")
            signers.append(account)
        return signers

    def save_deployment(self, contract_name: str, address: str, tx_hash: str):
        """
        保存部署信息

        Args:
            contract_name: 合约名称
            address: 合约地址
            tx_hash: 部署交易哈希
        """
        deployments = {}
        if self.deployments_file.exists():
            with open(self.deployments_file, 'r') as f:
                deployments = json.load(f)

        deployments[contract_name] = {
            'address': address,
            'tx_hash': tx_hash,
            'network': 'hardhat',
        }

        with open(self.deployments_file, 'w') as f:
            json.dump(deployments, f, indent=2)

        logger.info(f"部署信息已保存: {contract_name} -> {address}")

    def get_deployment_address(self, contract_name: str) -> Optional[str]:
        """
        获取部署地址

        Args:
            contract_name: 合约名称

        Returns:
            合约地址
        """
        if not self.deployments_file.exists():
            return None

        with open(self.deployments_file, 'r') as f:
            deployments = json.load(f)

        deployment = deployments.get(contract_name)
        return deployment.get('address') if deployment else None

    def start_node(self) -> subprocess.Popen:
        """
        启动 Hardhat 节点

        Returns:
            进程对象
        """
        process = subprocess.Popen(
            ["npx", "hardhat", "node"],
            cwd=self.project_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        logger.info("Hardhat 节点已启动")
        return process

    def run_script(self, script_path: str, network: str = "hardhat") -> bool:
        """
        运行 Hardhat 脚本

        Args:
            script_path: 脚本路径
            network: 网络名称

        Returns:
            是否成功
        """
        try:
            result = subprocess.run(
                ["npx", "hardhat", "run", script_path, "--network", network],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True
            )
            logger.info(f"脚本执行成功: {script_path}")
            logger.debug(result.stdout)
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"脚本执行失败: {e.stderr}")
            return False

    def get_gas_report(self) -> Optional[str]:
        """
        获取 Gas 报告

        Returns:
            Gas 报告内容
        """
        report_file = self.project_root / "reports" / "gas-report.txt"
        if not report_file.exists():
            return None

        with open(report_file, 'r') as f:
            return f.read()

    def clean(self) -> bool:
        """
        清理编译产物

        Returns:
            是否成功
        """
        try:
            result = subprocess.run(
                ["npx", "hardhat", "clean"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True
            )
            logger.info("清理成功")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"清理失败: {e.stderr}")
            return False
