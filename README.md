
# Bitcoin Wallet Balance Checker

This script allows you to check the balance of Bitcoin wallets listed in a file (wallet-addresses-list.txt). It queries the Blockchain.info API to fetch the balance of each wallet and provides the balance in BTC, USD, and INR. If a wallet has a balance greater than a specified threshold, it triggers a bell sound to alert the user.

# Usage

1. Add Bitcoin wallet addresses to the wallet-addresses-list.txt file, with each address on a new line.
2. Run the bitcoin-wallet-balance-checker.py script.
3. Upon execution, the script will check the balances of the listed wallets.
4. If a wallet has a balance greater than 0 BTC, it will trigger a bell sound and record the wallet address along with its balance in the wallet-address-with-balance.txt file.
5. The script also provides the balance in USD and INR.
6. Once the script finishes execution, it will display the total number of wallets scanned and the time taken.

# Files

1. bitcoin-wallet-balance-checker.py: The main Python script to check wallet balances.
2. bell-sound.mp3: Sound file used to trigger the alert sound.
3. wallet-addresses-list.txt: File containing the list of 4. Bitcoin wallet addresses to be checked.
4. wallet-address-with-balance.txt: Output file where wallet balances with timestamps are stored.

# Developer Information

Developed by: ~Noobacker  
Contact: [http://harshal-pimpalshende.vercel.app/](http://harshal-pimpalshende.vercel.app/)  
Bitcoin Address for Contributions: bc1qhr33ul6w65e3exnjjwfj7dddrnlp3fug4gggpy

# Disclaimer / Warning

It's important to note that this script is intended for educational purposes only. Please use it responsibly and do not engage in any illegal activities. Remember, tracking Bitcoin balances should be done ethically and with the consent of the involved parties. Misuse of this script for malicious purposes is strictly prohibited. I'm not responsible for any consequences arising from the misuse of this script.
