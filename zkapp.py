# app.py
import os
import sys
import json
import time
import argparse
from typing import Optional, Dict, Any
from web3 import Web3
from eth_utils import keccak

DEFAULT_RPC = os.environ.get("RPC_URL", "https://mainnet.infura.io/v3/YOUR_INFURA_KEY")

def get_contract_metadata(w3: Web3, address: str, block: str) -> Dict[str, Any]:
    """
    Fetch contract metadata such as code size, keccak hash, and nonce.
    """
    try:
        address = Web3.to_checksum_address(address)
        code = w3.eth.get_code(address, block_identifier=block)
        nonce = w3.eth.get_transaction_count(address, block_identifier=block)
        code_hash = Web3.keccak(code).hex() if code else None
        return {"size": len(code), "hash": code_hash, "nonce": nonce}
    except Exception as e:
        print(f"❌ Error fetching contract metadata for {address}: {e}")
        return {"size": 0, "hash": None, "nonce": None}

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="zk-bytecode-stability — check if a contract’s bytecode and deployment state remain stable over time (useful for Aztec/Zama auditing and general Web3 soundness verification)."
    )
    p.add_argument("--rpc", default=DEFAULT_RPC, help="EVM RPC URL (default from RPC_URL)")
    p.add_argument("--address", required=True, help="Contract address to monitor")
    p.add_argument("--from-block", type=int, required=True, help="Start block number")
    p.add_argument("--to-block", type=int, required=True, help="End block number")
    p.add_argument("--step", type=int, default=100000, help="Block step for sampling (default: 100000)")
    p.add_argument("--timeout", type=int, default=30, help="RPC timeout (seconds)")
    p.add_argument("--json", action="store_true", help="Output results as JSON")
    return p.parse_args()

def main() -> None:
    start = time.time()
    args = parse_args()

    if not Web3.is_address(args.address):
        print("❌ Invalid Ethereum address format.")
        sys.exit(1)

    w3 = Web3(Web3.HTTPProvider(args.rpc, request_kwargs={"timeout": args.timeout}))
    if not w3.is_connected():
        print("❌ RPC connection failed. Check your RPC_URL or --rpc argument.")
        sys.exit(1)

    print("🔧 zk-bytecode-stability")
    print(f"🔗 RPC: {args.rpc}")
    try:
        print(f"🧭 Chain ID: {w3.eth.chain_id}")
    except Exception:
        pass
    print(f"🏷️ Address: {args.address}")
    print(f"🧱 Block range: {args.from_block} → {args.to_block} (step {args.step})")

    metadata_history = []
    last_hash = None
    changes_detected = False

    for block in range(args.from_block, args.to_block + 1, args.step):
           print(f"🔎 Checking block {block} ...")
        
        meta = get_contract_metadata(w3, args.address, block)
        metadata_history.append({"block": block, **meta})

        if last_hash is None:
            last_hash = meta["hash"]
        elif meta["hash"] != last_hash:
            print(f"⚠️ Bytecode change detected at block {block}!")
            changes_detected = True
            last_hash = meta["hash"]

    print(f"📊 Sampled {len(metadata_history)} block points.")
    if changes_detected:
        print("🚨 Contract bytecode changed during the monitored range.")
    else:
        print("✅ Contract bytecode remained stable across all sampled blocks.")

    elapsed = time.time() - start
    print(f"⏱️ Completed in {elapsed:.2f}s")

    if args.json:
        result = {
            "address": Web3.to_checksum_address(args.address),
            "rpc": args.rpc,
            "chain_id": None,
            "from_block": args.from_block,
            "to_block": args.to_block,
            "step": args.step,
            "metadata": metadata_history,
            "changes_detected": changes_detected,
            "elapsed_seconds": round(elapsed, 2)
        }
        try:
            result["chain_id"] = w3.eth.chain_id
        except Exception:
            pass
        print(json.dumps(result, ensure_ascii=False, indent=2))

    sys.exit(0 if not changes_detected else 2)

if __name__ == "__main__":
    main()
