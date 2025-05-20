import logging
import paho.mqtt.client as mqtt
import paho.mqtt.enums as mqtt_enums
import threading

from app.core.config import Settings
from app.mqtt import create_on_mqtt_backup_message_handler
from app.startup_tasks.minio_client import _minio_client as minio_client
from typing import Optional

logger = logging.getLogger(__name__)  # Use module-level logger

_mqtt_client: Optional[mqtt.Client] = None
_mqtt_thread: Optional[threading.Thread] = None


# MQTT setup
def mqtt_listener(settings: Settings):
    global _mqtt_client
    _mqtt_client = mqtt.Client(callback_api_version=mqtt_enums.CallbackAPIVersion.VERSION2)
    _mqtt_client.on_message = create_on_mqtt_backup_message_handler(minio_client)
    logger.info(f"Connecting to MQTT broker on {settings.mqtt_host}:{settings.mqtt_port} ...")
    _mqtt_client.connect(settings.mqtt_host, settings.mqtt_port)
    _mqtt_client.subscribe("/biofield-signal/+/+")

    logger.info("Successfully connected to MQTT broker, looping forever..")

    _mqtt_client.loop_forever()


def start_mqtt_listener(settings: Settings):
    # Background MQTT thread
    global _mqtt_thread
    _mqtt_thread = threading.Thread(target=mqtt_listener(settings=settings), daemon=True)
    _mqtt_thread.start()


def exit_mqtt_listener():
    if _mqtt_client:
        logger.info("Disconnecting from the MQTT broker..")
        _mqtt_client.disconnect()
        _mqtt_client.loop_stop()
        logger.info("Successfully disconnected from the MQTT broker")
