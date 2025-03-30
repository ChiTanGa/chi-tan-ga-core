import time
from ib_insync import *

# Connect to IBKR TWS or IB Gateway
ib = IB()
#ib.connect('127.0.0.1', 7497, clientId=1)  # 7497 = Paper Trading, 7496 = Live
ib.connect('127.0.0.1', 4002, clientId=1)  # 7497 = Paper Trading, 7496 = Live

# Define Forex or CFD Contract
symbol = "USDCHF"  # Forex example: EURUSD, CFD example: "SPX500"
contract = Forex(symbol)  # Use CFD('SPX500') for CFD trading


# Get 10s trend direction
def get_trend():
    bars = ib.reqHistoricalData(
        contract,
        endDateTime='',
        durationStr='60 S',  # Last 10 seconds
        barSizeSetting='1 secs',
        whatToShow='MIDPOINT',
        useRTH=False
    )

    if len(bars) < 2:
        return None  # Not enough data

    start_price = bars[0].close
    end_price = bars[-1].close

    return "BUY" if end_price > start_price else "SELL"


# Place a market order
def place_trade(direction):
    order = MarketOrder(direction, 10000)  # 10,000 units = 0.1 lot
    trade = ib.placeOrder(contract, order)
    ib.waitOnUpdate()
    print(f"Placed {direction} order for {symbol}")
    return trade


# Trading Loop
while True:
    trade_direction = get_trend()

    if trade_direction:
        trade = place_trade(trade_direction)

        # Hold for 10 seconds
        time.sleep(10)

        # Close the position
        opposite_direction = "SELL" if trade_direction == "BUY" else "BUY"
        place_trade(opposite_direction)
        print(f"Closed {trade_direction} position after 10s")

    time.sleep(5)  # Wait before checking trend again
