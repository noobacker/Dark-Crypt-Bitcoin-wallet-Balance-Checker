# Dark-Crypt Scanner Suite

⚠️ **DISCLAIMER: I am NOT responsible for the misuse of this tool. This project is strictly for educational and research purposes (e.g., demonstrating the dangers of weak entropy and dictionary attacks). Any illegal use, unauthorized scanning, or theft of funds is strictly prohibited. Use at your own risk.** ⚠️

## Overview

The Dark-Crypt Scanner Suite is an advanced, multi-core cryptocurrency security research tool. It allows researchers to test the resilience of wallet generation algorithms, demonstrate the mathematical impossibility of brute-forcing true entropy, and highlight the extreme dangers of human-generated "weak" seed phrases via dictionary attacks.

All functionalities have been consolidated into a single, interactive application: `master-scanner.py`.

## Core Engines & Performance Architecture

### 1. Online API Scanner (Pure Entropy Brute-Force)
Generates completely random 12-word seed phrases using standard 128-bit entropy. It derives the cryptographic keys (BTC and ETH) and checks their balances live against public internet APIs.
* **Purpose:** Demonstrates that brute-forcing *true* randomness is mathematically impossible.
* **Optimization:** Utilizes `requests.Session()` for TCP Connection Pooling, significantly reducing HTTP handshake latency during rapid API calls.

### 2. Offline Collision Engine (Dictionary Attack)
Loads a massive database of funded accounts directly into your system's RAM. It uses a targeted dictionary attack to generate predictable, human-like phrases, deriving the addresses and instantly checking them against the offline database.
* **Purpose:** Demonstrates the severe vulnerabilities of using predictable passphrases or flawed random number generators.
* **Optimization:** Implements **Zero-IPC Copy-on-Write Memory Forking**. By bypassing standard Python multiprocessing manager bottlenecks, the RAM database is natively shared across all CPU cores, multiplying scanning speed by up to 50x compared to standard IPC.

### 3. Specific Address List Checker
Reads a user-provided list of Bitcoin addresses and queries their balances using a multi-API rotator to avoid instant rate limiting.

## The Mathematical Proof (Why We Built This)

The core objective of this project is to prove the resilience of modern cryptographic encryption. 

### How the Algorithm Works
This suite operates by generating 12-word seed phrases (using the BIP39 standard), running those phrases through HMAC-SHA512 hashing to derive the cryptographic master seed, and then using Elliptic Curve Cryptography (secp256k1) to calculate the final public wallet address. The script then instantly checks if that derived address matches any known funded addresses loaded into a massive, offline RAM database (simulating a Hash Set O(1) lookup).

### The Educational Conclusion
Even when utilizing the Offline Collision Engine—pushing modern, multi-core processors to their absolute thermal limits to check thousands of wallets per second—**you will likely never find a single wallet.** 

The mathematics of 128-bit entropy is practically unbreakable. To put it in perspective, guessing a truly random 12-word phrase would take a supercomputer quadrillions of years. 

If this suite *does* manage to find a collision, it is **strictly due to human custom error**. Humans often bypass true randomness to create "brainwallets" using predictable patterns (e.g., repeating the same word 12 times, or using song lyrics). The dictionary attack feature targets this specific human predictability. 

**This suite serves as a definitive, high-speed proof that cryptocurrency encryption algorithms are phenomenally secure, and that the only real vulnerability lies in weak human entropy and poor password practices.**

## Installation & Setup

1. **Prerequisites:** Ensure you have Python 3 installed.
2. **Install Dependencies:**
   ```bash
   pip install bit cashaddress eth-account requests mnemonic
   ```
3. **Database Setup (For Option 2 - Offline Engine):**
   Place your compressed database file (e.g., `Latest_BitcoinCash_Addresses.tsv.gz`) in the root directory.
   > **Note:** You can download updated rich address database files from: [Pymmdrza/Rich-Address-Wallet](https://github.com/Pymmdrza/Rich-Address-Wallet/tree/main)
4. **Custom Dictionary (For Option 2 - Offline Engine):**
   Open `dictionary-attack-words.txt` and add the specific words you want the script to use when building predictable phrases. It must contain at least 12 words.
5. **Custom Address List (For Option 3 - List Checker):**
   Add Bitcoin addresses to `wallet-addresses-list.txt` (one per line).

## Usage

Launch the interactive master suite:
```bash
python3 master-scanner.py
```

Follow the on-screen prompts to select your scanning method.

## Hardware Configuration
When utilizing the Offline Collision Engine, the script will prompt for hardware access to optimize performance based on your system's processor (e.g., Apple M1) and RAM. You can choose:
* **Safe Mode (1 Core):** Silent, safe background running.
* **Balanced Mode (Half Cores):** Recommended for stable, high-speed scanning without crashing the system.
* **Extreme Mode (Max Cores):** Maximum speed. May cause significant heating and fan noise. Will not permanently damage hardware.
* **Custom:** Manually allocate exactly how many CPU cores the script can use.

## Output Files
The suite automatically manages several log files:
* `simulated_breaches.txt`: Logs any collisions found during offline scanning.
* `all-scanned-wallets.txt`: Logs all generated phrases and addresses during online scanning.
* `non-zero-balance-wallets.txt`: Logs online accounts found with active balances.
* `scanner-stats.txt`: A live, real-time ticker updating your scanning speed, uptime, and total checks.

## Legacy Scripts
* `automated-scanner.py`, `bch-offline-scanner.py`, `bitcoin-wallet-balance-checker.py`: Earlier standalone versions of the tools (now completely merged into `master-scanner.py`).

## Contributing

We welcome contributions to improve the efficiency, architecture, and educational value of this suite. If you have performance optimizations (such as C-extensions for cryptographic derivation) or new API integrations, please feel free to submit a pull request or open an issue. All contributions must strictly adhere to the educational and ethical guidelines of this project.

## Developer Information

Developed by: ~Noobacker  
Contact: [http://harshal-pimpalshende.vercel.app/](http://harshal-pimpalshende.vercel.app/)  
Bitcoin Address for Contributions: bc1qhr33ul6w65e3exnjjwfj7dddrnlp3fug4gggpy

## Final Warning

It is important to reiterate that this script is intended for **educational purposes only**. Please use it responsibly and do not engage in any illegal activities. Tracking Bitcoin balances or generating keys must be done ethically and with the consent of the involved parties. Misuse of this script for malicious purposes is strictly prohibited. I am not responsible for any consequences arising from the misuse of this script.
