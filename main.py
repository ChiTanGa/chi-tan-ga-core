import time
import serial
from datetime import datetime
from pocketoptionapi import PocketOption
import logging
import os
import argparse
import curses
import threading

# Replace '/dev/tty.usbmodemXXXX' with the actual port name
# You can find this in the Arduino IDE under Tools > Port
# It often looks like /dev/tty.usbmodemXXXX or /dev/tty.usbserial-XXXX
serial_port_name = '/dev/tty.usbmodem1101'
#serial_port_name = '/dev/tty.wlan-debug' #For testing only
serial_port_baud_rate = 9600  # Match the baud rate with the Arduino code
serial_port = None  # Serial port used for communication

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


def update_stream_cb(_, message):
    timestamp = datetime.fromtimestamp(message[1])
    if serial_port is not None:
        print(f"Asset: {message[0]} Server time: {timestamp} Exchange rate: {message[2]}")
        serial_port.write(f"Exchange rate: {message[2]}")
    else:
        logging.info(f"Exchange rate: {message[2]}")


def connect_to_pocket_option_api_update_stream(active, seconds):
    logging.info("Connecting with SSID: %s", ssid)
    api = PocketOption(ssid, demo=True)

    # Connect to exchange data via Pocket Options
    api.connect()

    # Waiting for connection..
    while not api.check_connect():
        print("Waiting for connection next 5s...")
        time.sleep(5)

    print("Check connect: ", api.check_connect())
    print("Balance: ", api.get_balance())
    print("Server datetime: ", api.get_server_datetime())

    time.sleep(20)
    print(f"Exchange changing symbol to: {active} for {seconds}seconds")
    api.set_update_stream_callback(update_stream_cb)
    api.change_symbol(active, seconds)
    time.sleep(seconds)
    print(f"End of tracing symbol: {active}")
    api.disconnect()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to connect to Pocket Option API and optionally use a serial "
                                                 "port to write out exchange rates.")
    parser.add_argument("-tm", "--test-mode", action="store_true", help="Run the script in test mode without opening "
                                                                        "the serial port, writing results into "
                                                                        "standard output instead of serial port.")
    args = parser.parse_args()

    try:
        if not args.test_mode:
            # Open the serial connection
            serial_port = serial.Serial(serial_port_name, serial_port_baud_rate, timeout=1)
        else:
            # Fall back to standard output
            logging.warning("Using standard output instead of serial port")

        # Connect to Pocket API to get updates of exchange rates
        connect_to_pocket_option_api_update_stream(active="EURCHF_otc", seconds=50)

    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")

    except KeyboardInterrupt:
        print("Exiting program...")

    finally:
        # Close the serial connection
        if 'serial_port' in locals() and serial_port is not None and serial_port.is_open:
            serial_port.close()
