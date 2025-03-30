import time
import requests
from web3 import Web3
from dydx3 import Client
from eth_account.signers.local import LocalAccount

# 1. Connect to Ethereum RPC (Optimism/Arbitrum for low fees)
RPC_URL = "https://arb1.arbitrum.io/rpc"  # Arbitrum RPC
web3 = Web3(Web3.HTTPProvider(RPC_URL))

# 2. Set up wallet (Use a real private key for live trading)
PRIVATE_KEY = "YOUR_PRIVATE_KEY"
account: LocalAccount = web3.eth.account.from_key(PRIVATE_KEY)
WALLET_ADDRESS = account.address

# 3. Connect to dYdX API (Layer 2, no gas fees)
DYDX_API_KEY = "YOUR_DYDX_API_KEY"
DYDX_SECRET = "YOUR_DYDX_SECRET"
DYDX_PASSPHRASE = "YOUR_DYDX_PASSPHRASE"
dydx_client = Client(
    host="https://api.dydx.exchange",
    api_key=DYDX_API_KEY,
    api_secret=DYDX_SECRET,
    api_passphrase=DYDX_PASSPHRASE
)

# 4. Define trading pair (ETH-USDC)
PAIR = "ETH-USD"


# 5. Get last 20s price trend from dYdX
def get_trend():
    url = f"https://api.dydx.exchange/v3/candles/{PAIR}?resolution=1&limit=20"
    response = requests.get(url).json()
    candles = response['candles']

    if len(candles) < 2:
        return None  # Not enough data

    start_price = float(candles[0]['close'])
    end_price = float(candles[-1]['close'])

    return "BUY" if end_price > start_price else "SELL"


# 6. Place a trade on dYdX Layer 2
def place_trade(direction):
    # Define order size
    order_size = 0.01  # Example: 0.01 ETH

    # Place market order on dYdX
    order = dydx_client.private.create_order(
        market=PAIR,
        side="BUY" if direction == "BUY" else "SELL",
        size=order_size,
        type="MARKET",
        price="0",  # Market orders auto-fill
        post_only=False
    )
    print(f"Placed {direction} order for {order_size} ETH")


# 7. Main trading loop
while True:
    trade_direction = get_trend()
    if trade_direction:
        place_trade(trade_direction)

        # Hold for 30s, then exit
        time.sleep(30)
        opposite_direction = "SELL" if trade_direction == "BUY" else "BUY"
        place_trade(opposite_direction)
        print(f"Closed position after 30s")

    time.sleep(60)  # Wait 1 min before next trade
