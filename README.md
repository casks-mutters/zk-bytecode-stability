# zk-bytecode-stability

## Overview
This repository provides a simple command-line tool that checks if a smart contract’s **bytecode** and **state properties** (like nonce and code size) remain consistent across a range of blockchain blocks.  
It is particularly useful for detecting unauthorized redeployments or stealth upgrades in privacy or FHE ecosystems such as **Aztec** or **Zama**.

## Features
- Monitor contract bytecode over time  
- Detect redeployments or upgrades  
- Verify stability of contracts across blocks  
- Works with any EVM-compatible chain  
- JSON output for automated monitoring  

## Installation
1. Install Python 3.9+  
2. Install dependencies:
   pip install web3 eth-utils
3. Set your RPC endpoint:
   export RPC_URL=https://mainnet.infura.io/v3/YOUR_KEY
   
## Usage
Monitor a contract between two blocks:
   python app.py --address 0xYourContract --from-block 18000000 --to-block 19000000

Increase sampling resolution:
   python app.py --address 0xYourContract --from-block 18000000 --to-block 20000000 --step 50000

JSON output for CI systems:
   python app.py --address 0xYourContract --from-block 18000000 --to-block 19000000 --json

## Example Output
🔧 zk-bytecode-stability  
🔗 RPC: https://mainnet.infura.io/v3/YOUR_KEY  
🧭 Chain ID: 1  
🏷️ Address: 0x00000000219ab540356cBB839Cbe05303d7705Fa  
🧱 Block range: 18000000 → 19000000 (step 100000)  
📊 Sampled 11 block points.  
✅ Contract bytecode remained stable across all sampled blocks.  
⏱️ Completed in 0.72s  

### When a change is detected:
⚠️ Bytecode change detected at block 18500000!  
🚨 Contract bytecode changed during the monitored range.  
Exit code: 2  

## Notes
- For proxy contracts, this tool will detect changes at the proxy level, not the implementation address.  
- Combine with storage or state-root verification tools for complete soundness audits.  
- Works on Ethereum, L2 networks (Arbitrum, Optimism, Base), and private devnets.  
- Use a smaller `--step` for more granular analysis.  
- Can be scheduled to run daily in CI/CD to detect unauthorized upgrades.  
- Exit codes:  
  `0` → Bytecode stable  
  `2` → Detected bytecode changes or RPC errors.  
