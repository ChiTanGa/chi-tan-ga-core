import time
import datetime
from pocketoptionapi import PocketOption
import logging
import os

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')

# How to get SSID from Pocket Options
# https://www.youtube.com/watch?v=YpM5BeNFvaI&ab_channel=tradingbots
# 1) go to pocket options in your chrome - select the desired market - real/demo
# 2) go to chrome devtools, network tab, WS tab
# 3) click on any request and in messages tab filter for "auth"
# example SSID begins like: 42["auth",{"session":"a:4:{s:10:\"session_id\";s:32:\"10951......

# Read SSID from env variable (or use dotenv to read from local files if you have more environments)
ssid = os.getenv("SSID")
if ssid is None:
    logging.error("SSID environment variable is not set. Please set environment variable SSID")
    exit(-1)

logging.info("Connecting with SSID: %s", ssid)
api = PocketOption(ssid, demo=True)


def update_stream_cb(_, message):
    timestamp = datetime.fromtimestamp(message[1])
    print(f"Asset: {message[0]} Server time: {timestamp} Exchange rate: {message[2]}")


if __name__ == "__main__":
    api.connect()

    # Waiting for connection..
    while not api.check_connect():
        print("Waiting for connection next 5s...")
        time.sleep(5)

    print("Check connect: ", api.check_connect())

    print("Balance: ", api.get_balance())

    print("Server datetime: ", api.get_server_datetime())

    time.sleep(20)
    active = "EURCHF_otc"
    seconds = 50
    print(f"Exchange changing symbol to: {active} for {seconds}seconds")
    api.set_update_stream_callback(update_stream_cb)
    api.change_symbol(active, seconds)
    time.sleep(seconds)
    print(f"End of tracing symbol: {active}")
    api.disconnect()
