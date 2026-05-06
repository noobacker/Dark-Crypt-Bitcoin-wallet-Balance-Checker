"""
DARK-CRYPT SCANNER SUITE
========================
DISCLAIMER: This script is intended for EDUCATIONAL AND RESEARCH PURPOSES ONLY.
The author/developer is NOT RESPONSIBLE for any misuse of this tool, any illegal 
activities, or any consequences arising from its usage. Tracking and scanning 
cryptocurrency balances or generating keys without explicit consent is prohibited.
USE AT YOUR OWN RISK.
"""

import time
import os
import sys
import multiprocessing
import random
import gzip
import requests
import platform
import subprocess
import webbrowser
from mnemonic import Mnemonic

try:
    if sys.platform == "darwin":
        multiprocessing.set_start_method("fork")
except RuntimeError:
    pass

try:
    from bit import Key
    import cashaddress
    from eth_account import Account
except ImportError:
    print("Missing libraries. Run: /Library/Frameworks/Python.framework/Versions/3.10/bin/python3.10 -m pip install bit cashaddress eth-account requests mnemonic")
    sys.exit(1)

# --- GLOBAL CONFIGURATION ---
ALL_WALLETS_FILE = "all-scanned-wallets.txt"
NON_ZERO_WALLETS_FILE = "non-zero-balance-wallets.txt"
STATS_FILE = "scanner-stats.txt"
STATS_JS_FILE = "stats-data.js"
RESULTS_FILE = "simulated_breaches.txt"
DB_FILE_GZ = "Latest_BitcoinCash_Addresses.tsv.gz"
STATS_UPDATE_INTERVAL = 5
Account.enable_unaudited_hdwallet_features()

# Global database for copy-on-write memory sharing (eliminates IPC overhead)
GLOBAL_OFFLINE_DB = set()

# HTTP Session for TCP connection reuse
http_session = requests.Session()

# ==============================================================================
# 1. ONLINE SCANNER COMPONENTS
# ==============================================================================
BTC_APIS = [
    "https://blockchain.info/address/{address}?format=json",
    "https://blockstream.info/api/address/{address}",
    "https://mempool.space/api/address/{address}"
]
current_api_index = 0

def online_check_btc_balance(address):
    global current_api_index
    for _ in range(len(BTC_APIS)):
        url_template = BTC_APIS[current_api_index]
        url = url_template.format(address=address)
        try:
            response = http_session.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if "blockchain.info" in url:
                    return data.get("final_balance", 0) / 1e8
                elif "blockstream.info" in url or "mempool.space" in url:
                    chain_stats = data.get("chain_stats", {})
                    return (chain_stats.get("funded_txo_sum", 0) - chain_stats.get("spent_txo_sum", 0)) / 1e8
            current_api_index = (current_api_index + 1) % len(BTC_APIS)
        except:
            current_api_index = (current_api_index + 1) % len(BTC_APIS)
            continue
    return 0.0

def online_worker(worker_id, result_queue, seen_dict):
    mnemo = Mnemonic("english")
    while True:
        phrase = mnemo.generate(strength=128)
        phrase_hash = hash(phrase)
        if phrase_hash in seen_dict:
            continue
        seen_dict[phrase_hash] = True
        
        try:
            seed = mnemo.to_seed(phrase)
            btc_key = Key.from_int(int.from_bytes(seed[:32], 'big'))
            btc_addr = btc_key.address
            eth_acc = Account.from_mnemonic(phrase)
            eth_addr = eth_acc.address
            
            result_queue.put({'phrase': phrase, 'btc_addr': btc_addr, 'eth_addr': eth_addr})
        except:
            continue

def online_log_result(file_path, data):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_entry = (
        f"[{timestamp}] Phrase: {data['phrase']}\n"
        f"BTC Addr: {data['btc_addr']} | Balance: {data.get('btc_bal', 0):.8f}\n"
        f"ETH Addr: {data['eth_addr']} | Balance: {data.get('eth_bal', 0):.8f}\n"
        f"{'-'*60}\n"
    )
    with open(file_path, "a") as f:
        f.write(log_entry)

def run_online_scanner(num_processes):
    print(f"\n🚀 Starting Online API Scanner on {num_processes} cores...")
    manager = multiprocessing.Manager()
    seen_dict = manager.dict()
    
    webbrowser.open(DASHBOARD_URL)
    
    result_queue = multiprocessing.Queue(maxsize=1000)
    
    processes = []
    for i in range(num_processes):
        p = multiprocessing.Process(target=online_worker, args=(i, result_queue, seen_dict))
        p.daemon = True
        p.start()
        processes.append(p)

    count = 0
    start_time = time.time()
    
    try:
        while True:
            if not result_queue.empty():
                wallet = result_queue.get()
                count += 1
                
                btc_bal = online_check_btc_balance(wallet['btc_addr'])
                wallet['btc_bal'] = btc_bal
                wallet['eth_bal'] = 0.0
                
                online_log_result(ALL_WALLETS_FILE, wallet)
                
                if btc_bal > 0:
                    print(f"\n[!] ALERT: Found {btc_bal} BTC at {wallet['btc_addr']}")
                    online_log_result(NON_ZERO_WALLETS_FILE, wallet)
                    if sys.platform == "darwin": os.system("afplay bell-sound.mp3")
                
                speed = count / max((time.time() - start_time), 1)
                print(f"\r⚡ Online Speed: ~{speed:.1f}/sec | Checked: {count:,} ", end="", flush=True)
                time.sleep(0.05)
            else:
                time.sleep(0.01)
    except KeyboardInterrupt:
        print("\n🛑 Stopping Online Scanner...")
        for p in processes: p.terminate()

# ==============================================================================
# 2. OFFLINE COLLISION ENGINE COMPONENTS
# ==============================================================================
def load_offline_database():
    global GLOBAL_OFFLINE_DB
    print(f"⚙️  Loading addresses from {DB_FILE_GZ} into RAM...")
    start_load = time.time()
    GLOBAL_OFFLINE_DB.clear()
    
    try:
        with gzip.open(DB_FILE_GZ, 'rt') as f:
            first_line = f.readline()
            if "address" not in first_line.lower():
                parts = first_line.strip().split(',')
                if len(parts) > 0: GLOBAL_OFFLINE_DB.add(parts[0].replace('bitcoincash:', ''))
            
            count = 1
            for line in f:
                parts = line.strip().split(',')
                if len(parts) > 0:
                    GLOBAL_OFFLINE_DB.add(parts[0].replace('bitcoincash:', ''))
                    
                count += 1
                # Update terminal every 500k lines so the user knows it's not stuck
                if count % 500000 == 0:
                    elapsed = time.time() - start_load
                    print(f"\r⏳ Still reading file... {count:,} lines processed ({elapsed:.1f}s elapsed)", end="", flush=True)
                    
        print(f"\n✅ Loaded {len(GLOBAL_OFFLINE_DB):,} active addresses into RAM in {time.time()-start_load:.2f} seconds.")
        return True
    except Exception as e:
        print(f"\n❌ Error loading database: {e}")
        return False

def load_attack_dictionary():
    dict_file = "dictionary-attack-words.txt"
    if not os.path.exists(dict_file):
        print(f"\n❌ Error: '{dict_file}' not found.")
        print("Please create this file and add the BIP39 words you want to use for the dictionary attack.")
        sys.exit(1)
        
    with open(dict_file, "r") as f:
        words = [line.strip().lower() for line in f if line.strip()]
        
    if len(words) < 12:
        print(f"\n⚠️ Warning: Your dictionary only has {len(words)} words. You need at least 12 words to form a valid phrase.")
        sys.exit(1)
    
    return words

def offline_worker(worker_id, result_queue, scan_counter, attack_dictionary):
    mnemo = Mnemonic("english")
    local_count = 0
    
    while True:
        phrase = " ".join(random.choices(attack_dictionary, k=12))
        if mnemo.check(phrase):
            try:
                seed = mnemo.to_seed(phrase)
                btc_key = Key.from_int(int.from_bytes(seed[:32], 'big'))
                legacy_address = btc_key.address
                bch_address = cashaddress.convert.to_cash_address(legacy_address)
                clean_bch_addr = bch_address.replace('bitcoincash:', '')
                
                if clean_bch_addr in GLOBAL_OFFLINE_DB:
                    result_queue.put({'phrase': phrase, 'address': bch_address})
                    
                local_count += 1
                if local_count >= 100:
                    with scan_counter.get_lock(): scan_counter.value += local_count
                    local_count = 0
            except:
                pass

def run_offline_scanner(num_processes):
    attack_dictionary = load_attack_dictionary()
    print(f"📚 Loaded custom dictionary with {len(attack_dictionary)} words.")
    
    success = load_offline_database()
    if not success: return
        
    print(f"\n🚀 Launching Offline Collision Engine across {num_processes} cores...")
    print("⚡ Memory Optimization Active: Bypassing IPC via copy-on-write memory forking.")
    
    webbrowser.open(DASHBOARD_URL)
    
    result_queue = multiprocessing.Queue()
    scan_counter = multiprocessing.Value('i', 0)
    processes = []
    
    for i in range(num_processes):
        p = multiprocessing.Process(target=offline_worker, args=(i, result_queue, scan_counter, attack_dictionary))
        p.daemon = True
        p.start()
        processes.append(p)

    start_time = time.time()
    last_stats_time = start_time
    
    try:
        while True:
            elapsed = time.time() - start_time
            current_scans = scan_counter.value
            
            print(f"\r⚡ Speed: ~{current_scans/max(elapsed,1):.0f}/sec | Checked: {current_scans:,} ", end="")
            
            if time.time() - last_stats_time > STATS_UPDATE_INTERVAL:
                stats_content = (
                    f"--- OFFLINE SCANNER STATISTICS ---\n"
                    f"Last Updated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"Total Wallets Checked: {current_scans:,}\n"
                    f"Uptime: {int(elapsed // 3600)}h {int((elapsed % 3600) // 60)}m {int(elapsed % 60)}s\n"
                    f"Average Speed: {current_scans/max(elapsed,1):.2f} checks/sec\n"
                    f"Database Size: {len(GLOBAL_OFFLINE_DB):,} Addresses in RAM (Zero-IPC Mode)\n"
                    f"----------------------------------\n"
                )
                with open(STATS_FILE, "w") as f: f.write(stats_content)
                with open(STATS_JS_FILE, "w") as f:
                    safe_content = stats_content.replace('`', '\\`')
                    f.write(f"window.scannerStats = `{safe_content}`;")
                last_stats_time = time.time()
            
            if not result_queue.empty():
                match = result_queue.get()
                print(f"\n\n🚨 BREACH DETECTED 🚨")
                print(f"Address: {match['address']} | Phrase: {match['phrase']}")
                with open(RESULTS_FILE, "a") as f:
                    f.write(f"[{time.strftime('%H:%M:%S')}] BREACH: {match['address']} | PHRASE: {match['phrase']}\n")
                
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n🛑 Stopping Offline Scanner...")
        for p in processes: p.terminate()

# ==============================================================================
# 3. ADDRESS LIST CHECKER (Original Script Functionality)
# ==============================================================================
def run_address_list_checker():
    input_file = "wallet-addresses-list.txt"
    if not os.path.exists(input_file):
        print(f"\n❌ Error: '{input_file}' not found.")
        print("Please create this file and add Bitcoin addresses (one per line) before running this option.")
        return

    print(f"\n🚀 Starting Address List Checker (Reading from {input_file})...")
    
    with open(input_file, "r") as f:
        addresses = [line.strip() for line in f if line.strip()]
        
    if not addresses:
        print("The list is empty. Add some addresses first!")
        return

    print(f"Loaded {len(addresses)} addresses to check.\n")
    
    for i, address in enumerate(addresses):
        print(f"[{i+1}/{len(addresses)}] Checking: {address} ... ", end="", flush=True)
        balance = online_check_btc_balance(address)
        
        if balance > 0:
            print(f"💰 FOUND: {balance:.8f} BTC")
            with open("wallet-address-with-balance.txt", "a") as out_f:
                out_f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] FOUND BALANCE: {balance:.8f} BTC | Address: {address}\n")
            if sys.platform == "darwin": os.system("afplay bell-sound.mp3")
        else:
            print("0 BTC")
            
        time.sleep(1) # Sleep to avoid instant rate limiting

# ==============================================================================
# HARDWARE CONFIGURATION & UX
# ==============================================================================
import platform
import subprocess

def get_processor_name():
    if sys.platform == "darwin":
        try:
            return subprocess.check_output(["sysctl", "-n", "machdep.cpu.brand_string"]).strip().decode("utf-8")
        except:
            pass
    return platform.processor() or platform.machine()

def get_system_info():
    cores = multiprocessing.cpu_count()
    try:
        ram_bytes = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')
        ram_gb = round(ram_bytes / (1024.**3))
    except:
        ram_gb = "Unknown"
    cpu_name = get_processor_name()
    return cpu_name, cores, ram_gb

def configure_hardware(is_offline=True):
    print("\n" + "-"*50)
    auth = input("⚠️  Permission requested to scan system hardware for optimization. Allow? (y/n): ")
    if auth.lower() != 'y':
        print("Hardware scan declined. Defaulting to Safe Mode (1 Core).")
        return 1
        
    cpu_name, cores, ram_gb = get_system_info()
    print("\n🔍 SYSTEM HARDWARE SCAN COMPLETE")
    print(f"   Processor: {cpu_name}")
    print(f"   Processor Cores Available: {cores}")
    print(f"   System RAM Detected: {ram_gb} GB")
    print("-" * 50)
    
    if not is_offline:
        print("\nNote: You selected the Online Scanner. Speed is heavily limited by internet APIs, not CPU.")
        base_speed = 5
    else:
        print("\nNote: Offline scanning relies completely on CPU cryptography. (RAM is also used, but requires ~1-2GB fixed).")
        base_speed = 500

    print("\nPlease select hardware usage level:")
    
    # Option 1: Safe
    print(f"1. Safe Mode (1 Core)")
    print(f"   Predicted Speed: ~{base_speed} checks/sec")
    print(f"   Safety Status: TOTALLY SAFE. System will stay cool. No restart or damage risk.\n")
    
    # Option 2: Balanced
    half_cores = max(2, cores // 2)
    print(f"2. Balanced Mode ({half_cores} Cores)")
    print(f"   Predicted Speed: ~{half_cores * base_speed} checks/sec")
    print(f"   Safety Status: RECOMMENDED. System is safe, won't crash or permanently damage hardware.\n")
    
    # Option 3: Extreme
    print(f"3. Extreme Mode ({cores} Cores)")
    print(f"   Predicted Speed: ~{cores * base_speed} checks/sec")
    print(f"   Safety Status: EXTREME. Might overheat, cause fans to spin loudly, or trigger thermal throttling/OS restart. WILL NOT permanently damage hardware.\n")
    
    # Option 4: Custom
    print(f"4. Custom Core Allocation (Enter manually)\n")
    
    while True:
        choice = input("Select usage level (1-4): ")
        if choice == '1': return 1
        elif choice == '2': return half_cores
        elif choice == '3': return cores
        elif choice == '4':
            while True:
                try:
                    custom = int(input(f"Enter number of cores to use (1-{cores}): "))
                    if 1 <= custom <= cores:
                        return custom
                    print(f"Please enter a number between 1 and {cores}.")
                except ValueError:
                    print("Please enter a valid number.")
        else: print("Invalid choice.")

# ==============================================================================
# MAIN MENU
# ==============================================================================
def main_menu():
    while True:
        print("\n" + "="*70)
        print("                 DARK-CRYPT SCANNER SUITE v1.0")
        print("="*70)
        print(" ⚠️  DISCLAIMER: I am NOT responsible for the misuse of this tool.")
        print("    This project is strictly for educational/research purposes.")
        print("    Any illegal use is prohibited. Use at your own risk.")
        print("="*70)
        
        print("\n" + "🌟 "*23)
        print("   LIVE UI DASHBOARD AVAILABLE!")
        print(f"   Cmd+Click link to open: \033[96m{DASHBOARD_URL}\033[0m")
        print("🌟 "*23 + "\n")
        
        print("1. Online API Scanner (Live checking, lower speed)")
        print("2. Offline Collision Engine (RAM database, ultra-high speed)")
        print("3. Check Specific Address List (From wallet-addresses-list.txt)")
        print("4. Exit")
        
        choice = input("\nSelect an option (1-4): ")
        
        if choice == '1':
            global NUM_PROCESSES_ONLINE
            NUM_PROCESSES_ONLINE = configure_hardware(is_offline=False)
            run_online_scanner(NUM_PROCESSES_ONLINE)
        elif choice == '2':
            global NUM_PROCESSES_OFFLINE
            NUM_PROCESSES_OFFLINE = configure_hardware(is_offline=True)
            run_offline_scanner(NUM_PROCESSES_OFFLINE)
        elif choice == '3':
            run_address_list_checker()
        elif choice == '4':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please select 1, 2, 3, or 4.")

if __name__ == "__main__":
    multiprocessing.freeze_support()
    
    import threading
    import http.server
    import socketserver
    
    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format, *args): pass
        
    port = 8080
    while True:
        try:
            httpd = socketserver.TCPServer(("", port), QuietHandler)
            threading.Thread(target=httpd.serve_forever, daemon=True).start()
            break
        except OSError:
            port += 1
            
    global DASHBOARD_URL
    DASHBOARD_URL = f"http://localhost:{port}/stats-dashboard.html"
    
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
