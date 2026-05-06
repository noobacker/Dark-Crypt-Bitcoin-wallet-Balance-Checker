# Graph Report - .  (2026-05-06)

## Corpus Check
- Corpus is ~927 words - fits in a single context window. You may not need a graph.

## Summary
- 17 nodes · 22 edges · 3 communities detected
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 2 edges (avg confidence: 0.82)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Project Metadata & Disclaimers|Project Metadata & Disclaimers]]
- [[_COMMUNITY_Runtime Behavior & APIs|Runtime Behavior & APIs]]
- [[_COMMUNITY_Script Structure|Script Structure]]

## God Nodes (most connected - your core abstractions)
1. `Bitcoin Wallet Balance Checker (project)` - 7 edges
2. `check_balance` - 5 edges
3. `main script` - 4 edges
4. `wallet-address-with-balance.txt (output)` - 4 edges
5. `check_balance()` - 3 edges
6. `wallet-addresses-list.txt (input)` - 3 edges
7. `play_bell_sound()` - 2 edges
8. `get_exchange_rates()` - 2 edges
9. `play_bell_sound` - 2 edges
10. `get_exchange_rates` - 2 edges

## Surprising Connections (you probably didn't know these)
- `Bitcoin Wallet Balance Checker (project)` --references--> `bell-sound.mp3`  [EXTRACTED]
  README.md → bitcoin-wallet-balance-checker.py
- `check_balance` --shares_data_with--> `wallet-address-with-balance.txt (output)`  [EXTRACTED]
  bitcoin-wallet-balance-checker.py → wallet-address-with-balance.txt
- `main script` --shares_data_with--> `wallet-addresses-list.txt (input)`  [EXTRACTED]
  bitcoin-wallet-balance-checker.py → wallet-addresses-list.txt
- `main script` --shares_data_with--> `wallet-address-with-balance.txt (output)`  [EXTRACTED]
  bitcoin-wallet-balance-checker.py → wallet-address-with-balance.txt
- `Bitcoin Wallet Balance Checker (project)` --references--> `main script`  [EXTRACTED]
  README.md → bitcoin-wallet-balance-checker.py

## Hyperedges (group relationships)
- **Wallet balance check flow** — wallet_addresses_list_input, bitcoin_wallet_balance_checker_check_balance, bitcoin_wallet_balance_checker_blockchain_info_api, bitcoin_wallet_balance_checker_coindesk_api, wallet_address_with_balance_output [INFERRED 0.85]

## Communities

### Community 0 - "Project Metadata & Disclaimers"
Cohesion: 0.43
Nodes (7): main script, Educational-purpose disclaimer, BTC donation address bc1qhr33ul..., Noobacker (developer), Bitcoin Wallet Balance Checker (project), wallet-address-with-balance.txt (output), wallet-addresses-list.txt (input)

### Community 1 - "Runtime Behavior & APIs"
Cohesion: 0.33
Nodes (6): bell-sound.mp3, blockchain.info API, check_balance, CoinDesk BPI API, get_exchange_rates, play_bell_sound

### Community 2 - "Script Structure"
Cohesion: 0.83
Nodes (3): check_balance(), get_exchange_rates(), play_bell_sound()

## Knowledge Gaps
- **5 isolated node(s):** `blockchain.info API`, `CoinDesk BPI API`, `Noobacker (developer)`, `Educational-purpose disclaimer`, `BTC donation address bc1qhr33ul...`
  These have ≤1 connection - possible missing edges or undocumented components.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Bitcoin Wallet Balance Checker (project)` connect `Project Metadata & Disclaimers` to `Runtime Behavior & APIs`?**
  _High betweenness centrality (0.278) - this node is a cross-community bridge._
- **Why does `check_balance` connect `Runtime Behavior & APIs` to `Project Metadata & Disclaimers`?**
  _High betweenness centrality (0.264) - this node is a cross-community bridge._
- **What connects `blockchain.info API`, `CoinDesk BPI API`, `Noobacker (developer)` to the rest of the system?**
  _5 weakly-connected nodes found - possible documentation gaps or missing edges._