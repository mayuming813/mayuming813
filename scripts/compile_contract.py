#!/usr/bin/env python3
"""
产出：contracts/abi/<ContractName>.json（ABI）、contracts/build/<ContractName>.json（ABI+bytecode 供部署用）。
"""
from pathlib import Path
import json
import sys

# 项目根目录
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

def main():
    import solcx

    contract_name = "SepoliaClaimFaucet"
    sol_file = ROOT / "contracts" / "temp_core_flow.sol"
    abi_dir = ROOT / "contracts" / "abi"
    build_dir = ROOT / "contracts" / "build"

    if not sol_file.exists():
        print(f"未找到合约文件: {sol_file}")
        sys.exit(1)

    abi_dir.mkdir(parents=True, exist_ok=True)
    build_dir.mkdir(parents=True, exist_ok=True)

    # 安装并指定 solc 版本（与合约 pragma ^0.8.20 一致）
    solcx.install_solc("0.8.20")
    compiled = solcx.compile_files(
        [str(sol_file)],
        output_values=["abi", "bin"],
        solc_version="0.8.20",
    )

    # 键格式通常为 "contracts/temp_core_flow.sol:SepoliaClaimFaucet" 或 "temp_core_flow.sol:SepoliaClaimFaucet"
    key = None
    for k in compiled:
        if f":{contract_name}" in k or k == contract_name:
            key = k
            break
    if not key:
        key = list(compiled.keys())[0]

    data = compiled[key]
    abi = data["abi"]
    bytecode = data["bin"]

    # 写入 ABI（供单测/接口测试加载）
    abi_path = abi_dir / f"{contract_name}.json"
    with open(abi_path, "w", encoding="utf-8") as f:
        json.dump(abi, f, indent=2, ensure_ascii=False)
    print(f"ABI 已写入: {abi_path}")

    # 写入 build（供部署脚本读取）
    build_path = build_dir / f"{contract_name}.json"
    with open(build_path, "w", encoding="utf-8") as f:
        json.dump({"abi": abi, "bytecode": bytecode}, f, indent=2, ensure_ascii=False)
    print(f"构建产物已写入: {build_path}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
