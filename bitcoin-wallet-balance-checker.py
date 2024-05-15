import sys
import re
import requests
import os
from time import sleep, strftime, localtime, time

# Bell-sound when wallet is found with balance
def play_bell_sound():
    os.system("afplay bell-sound.mp3")  

# Function to get current exchange rates for Bitcoin to USD and INR
def get_exchange_rates():
    usd_url = "https://api.coindesk.com/v1/bpi/currentprice/USD.json"
    inr_url = "https://api.coindesk.com/v1/bpi/currentprice/INR.json"
    try:
        usd_response = requests.get(usd_url)
        usd_rate = usd_response.json()["bpi"]["USD"]["rate_float"]
        inr_response = requests.get(inr_url)
        inr_rate = inr_response.json()["bpi"]["INR"]["rate_float"]
        return usd_rate, inr_rate
    except requests.RequestException as e:
        print(f"Failed to fetch exchange rates: {e}")
        return None, None

# Function to check balance
def check_balance(address, file_positions):
    SONG_BELL = True
    WARN_WAIT_TIME = 0
    SATOSHIS_PER_BTC = 1e+8
    MINIMUM_BALANCE = 0

    check_address = re.match(r' *([a-zA-Z1-9]{1,34})', address).group(1)

    try:
        response = requests.get(f"https://blockchain.info/address/{check_address}?format=json", timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
    except requests.RequestException as e:
        print(f"Failed to fetch balance for {check_address}: {e}")
        return

    print(f"\nBitcoin Address = {check_address}")

    try:
        blockchain_info_array = [float(data[tag]) for tag in ('total_received', 'final_balance')]
    except KeyError as e:
        print(f"Error: Missing key '{e}' in blockchain data.")
        return

    usd_rate, inr_rate = get_exchange_rates()
    if usd_rate is None or inr_rate is None:
        print("Exchange rates unavailable. Skipping balance conversion.")
        return

    for tag, btc_tokens in zip(('total_received', 'final_balance'), blockchain_info_array):
        print(f"{tag} \t= ", end='')
        if btc_tokens > 0.0:
            balance_usd = btc_tokens / SATOSHIS_PER_BTC * usd_rate
            balance_inr = btc_tokens / SATOSHIS_PER_BTC * inr_rate
            print(f"{btc_tokens / SATOSHIS_PER_BTC:.8f} Bitcoin (USD: ${balance_usd:.2f}, INR: ₹{balance_inr:.2f})")
            if btc_tokens > MINIMUM_BALANCE:
                play_bell_sound()
        else:
            print("0 Bitcoin")

        if SONG_BELL and tag == 'final_balance' and btc_tokens > 0.0:
            sys.stdout.write('\a\a\a')
            sys.stdout.flush()

            with open('wallet-address-with-balance.txt', 'a') as arq1:
                file_position = arq1.tell()
                file_positions.append(file_position)
                arq1.write(f"\nDate: {strftime('%Y-%m-%d %H:%M:%S', localtime())}")
                arq1.write(f"\nBitcoin Address: {check_address}")
                arq1.write(f"\t Balance: {btc_tokens / SATOSHIS_PER_BTC:.8f} Bitcoin (USD: ${balance_usd:.2f}, INR: ₹{balance_inr:.2f})\n")
            if WARN_WAIT_TIME > 0:
                sleep(WARN_WAIT_TIME)

# Main code
file_positions = []
start_time = time()
with open("wallet-addresses-list.txt") as file:
    for line in file:
        address = line.strip()
        print("__________________________________________________\n")
        print(f"Time: {strftime('%Y-%m-%d %H:%M:%S', localtime())}")
        check_balance(address, file_positions)

end_time = time()
total_time = end_time - start_time
hours = int(total_time // 3600)
minutes = int((total_time % 3600) // 60)
seconds = int(total_time % 60)
print("__________________________________________________\n")
with open('wallet-address-with-balance.txt', 'a') as arq1:
    arq1.write(f"Total wallet scanned = {len(file_positions)}\n")
    arq1.write(f"In {hours} hour(s) {minutes} minute(s) {seconds} second(s)\n")

print("__________________________________________________\n")
print("Developed by: ~Noobacker")
print("My contact on reddit: https://harshal-pimpalshende.vercel.app\n")
bitcoin_address = "bc1qhr33ul6w65e3exnjjwfj7dddrnlp3fug4gggpy"
print(f"Developed by: ~Noobacker. If you have found this to be beneficial and time-saving, we kindly ask you to consider making a contribution to support our ongoing efforts. Contributions can be sent to the following Bitcoin address: {bitcoin_address}")
with open('wallet-address-with-balance.txt', 'a') as arq1:
    arq1.write(f"\nDeveloped by: ~Noobacker. If you have found this to be beneficial and time-saving, we kindly ask you to consider making a contribution to support our ongoing efforts. Contributions can be sent to the following Bitcoin address: {bitcoin_address}")
