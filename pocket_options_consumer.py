import logging
import os
import time
from datetime import datetime

from pocketoptionapi import PocketOption

logger = logging.getLogger(__name__)


async def exchange_rate_pocket_options_consumer():
    # Read SSID from env variable (or use dotenv to read from local files if you have more environments)
    ssid = os.getenv("SSID")
    if ssid is None:
        logger.error("SSID environment variable is not set. Please set environment variable SSID")
        exit(-1)

    logger.info("Connecting with SSID: %s", ssid)
    api = PocketOption(ssid, demo=True)

    api.connect()

    # Waiting for connection..
    while not api.check_connect():
        logger.info("Waiting for connection next 5s...")
        time.sleep(5)

    logger.info("Check connect: ", api.check_connect())

    logger.info("Balance: ", api.get_balance())

    logger.info("Server datetime: ", api.get_server_datetime())

    time.sleep(20)
    active = "EURCHF_otc"
    seconds = 50
    logger.info(f"Exchange changing symbol to: {active} for {seconds}seconds")
    api.set_update_stream_callback(exchange_rate_pocket_options_update_callback)
    api.change_symbol(active, seconds)
    time.sleep(seconds)
    logger.info(f"End of tracing symbol: {active}")
    api.disconnect()


def exchange_rate_pocket_options_update_callback(_, message):
    timestamp = datetime.fromtimestamp(message[1])
    logger.info(f"Asset: {message[0]} Server time: {timestamp} Exchange rate: {message[2]}")
