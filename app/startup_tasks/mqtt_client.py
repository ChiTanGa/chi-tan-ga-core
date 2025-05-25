import logging
import sys
import paho.mqtt.client as mqtt
import paho.mqtt.enums as mqtt_enums
import threading
import time

from minio import Minio

from app.core.config import Settings
from app.mqtt import create_on_mqtt_backup_message_handler
from typing import Optional

logger = logging.getLogger(__name__)  # Use module-level logger

_mqtt_client: Optional[mqtt.Client] = None
_mqtt_thread: Optional[threading.Thread] = None


# MQTT setup
def mqtt_listener(settings: Settings, minio_client: Minio):
    global _mqtt_client
    _mqtt_client = mqtt.Client(callback_api_version=mqtt_enums.CallbackAPIVersion.VERSION1,
                               protocol=mqtt_enums.MQTTProtocolVersion.MQTTv31)
    _mqtt_client.on_message = create_on_mqtt_backup_message_handler(settings=settings, minio_client=minio_client)

    def _on_connect(client, userdata, flags, rc, properties=None):
        if rc == 0:
            logger.info("MQTT client connected successfully!")

            logger.info(f"Subscribing to MQTT topics: /{settings.mqtt_topic_root}/+/+")
            _mqtt_client.subscribe(f"/{settings.mqtt_topic_root}/+/+")

            logger.info("Successfully connected to MQTT broker, looping forever..")
            _mqtt_client.loop_forever()
        else:
            logger.error(f"MQTT client failed to connect, return code {rc}")
            exit(-1)
    _mqtt_client.on_connect = _on_connect

    logger.info(f"Connecting to MQTT broker on {settings.mqtt_host}:{settings.mqtt_port} ...")
    try:
        _mqtt_client.connect(settings.mqtt_host, settings.mqtt_port, keepalive=60)
        logger.info(f"is connected: {_mqtt_client.is_connected()}")
    except Exception as e:
        logger.error(f"Error during MQTT client connect: {e}")
        _mqtt_client.disconnect()
        sys.exit(-1)


def mqtt_listener2(settings: Settings, minio_client: Minio):
    global _mqtt_client
    _mqtt_client = mqtt.Client(callback_api_version=mqtt_enums.CallbackAPIVersion.VERSION2,
                               protocol=mqtt_enums.MQTTProtocolVersion.MQTTv5,
                               client_id="chi-tan-ga-mqtt-client")
    _mqtt_client.on_message = create_on_mqtt_backup_message_handler(settings=settings, minio_client=minio_client)

    def _on_connect(client, userdata, flags, rc, properties=None):
        if rc == 0:
            logger.info("MQTT client connected successfully!")

            logger.info(f"Subscribing to MQTT topics: /{settings.mqtt_topic_root}/+/+")
            _mqtt_client.subscribe(f"/{settings.mqtt_topic_root}/+/+")

            logger.info("Successfully connected to MQTT broker, looping forever..")
            _mqtt_client.loop_forever()
        else:
            logger.error(f"MQTT client failed to connect, return code {rc}")
            exit(-1)

    def _on_log(client, _, p, msg):
        logger.info(msg)
    _mqtt_client.on_connect = _on_connect
    _mqtt_client.on_log = _on_log
    logger.info(f"Connecting to MQTT broker on {settings.mqtt_host}:{settings.mqtt_port} ...")
    try:
        _mqtt_client.connect(settings.mqtt_host, settings.mqtt_port, keepalive=60)
        logger.info(f"is connected: {_mqtt_client.is_connected()}")
    except Exception as e:
        logger.error(f"Error during MQTT client connect: {e}")
        _mqtt_client.disconnect()
        sys.exit(-1)


def mqtt_listener3(settings: Settings, minio_client: Minio):
    global _mqtt_client
    _mqtt_client = mqtt.Client(
        callback_api_version=mqtt_enums.CallbackAPIVersion.VERSION2,
        protocol=mqtt_enums.MQTTProtocolVersion.MQTTv311,
        client_id="chi-tan-ga-mqtt-client"
    )

    def _on_connect(client, userdata, flags, reason_code, properties=None):
        if reason_code == 0:
            logger.info("MQTT client connected successfully!")
            topic = f"/{settings.mqtt_topic_root}/+/+"
            logger.info(f"Subscribing to MQTT topic: {topic}")
            client.subscribe(topic)
        else:
            logger.error(f"MQTT connect failed with code: {reason_code}")

    def _on_log(client, userdata, level, buf):
        logger.info(f"[MQTT] {buf}")

    _mqtt_client.on_connect = _on_connect
    _mqtt_client.on_log = _on_log
    _mqtt_client.on_message = create_on_mqtt_backup_message_handler(
        settings=settings, minio_client=minio_client)

    logger.info(f"Connecting to MQTT broker at {settings.mqtt_host}:{settings.mqtt_port} ...")

    try:
        _mqtt_client.connect(settings.mqtt_host, settings.mqtt_port, keepalive=60)
        #_mqtt_client.loop_forever()
        _mqtt_client.loop_start()

        # Wait (up to a few seconds) for connection
        for _ in range(40):
            if _mqtt_client.is_connected():
                break
            time.sleep(0.25)
        else:
            logger.error("MQTT client failed to connect within timeout")
            _mqtt_client.disconnect()
            sys.exit(1)

    except Exception as e:
        logger.exception(f"Error during MQTT client connect: {e}")
        _mqtt_client.disconnect()
        sys.exit(1)


def start_mqtt_listener(settings: Settings, minio_client: Minio):
    # Background MQTT thread
    global _mqtt_thread
    _mqtt_thread = threading.Thread(target=mqtt_listener3, args=(settings, minio_client,), daemon=True)
    _mqtt_thread.start()


def exit_mqtt_listener():
    if _mqtt_client:
        logger.info("Disconnecting from the MQTT broker..")
        _mqtt_client.disconnect()
        _mqtt_client.loop_stop()
        logger.info("Successfully disconnected from the MQTT broker")
