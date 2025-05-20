import logging
import msgpack
import json
from datetime import datetime
from io import BytesIO
from minio import Minio
from app.core import settings

logger = logging.getLogger(__name__)  # Use module-level logger


# Creates MQTT message handler with injected minio client dependency
def create_on_mqtt_backup_message_handler(minio_client: Minio):
    def handler(client, userdata, msg):
        _on_mqtt_backup_message_handler(client, userdata, msg, minio_client)

    return handler


# MQTT handler
def _on_mqtt_backup_message_handler(client, userdata, msg, minio_client):
    try:
        print(f"Received message on topic: {msg.topic}")
        parts = msg.topic.strip("/").split("/")
        if len(parts) != 3:
            print("Invalid topic format.")
            return

        _, device_name, sensor_name = parts

        # Unpack message with msgpack
        unpacked = msgpack.unpackb(msg.payload, raw=False)
        metadata = unpacked.get("metadata", {})
        file_data = unpacked.get("file", b"")

        # Timestamp for directory naming
        timestamp = datetime.utcnow()
        time_path = timestamp.strftime("%Y/%m/%d/%H-%M")

        base_path = f"{device_name}/{sensor_name}/{time_path}"
        metadata_path = f"{base_path}/metadata.json"
        file_path = f"{base_path}/data.h5"

        # Upload metadata
        metadata_bytes = BytesIO(json.dumps(metadata).encode("utf-8"))
        minio_client.put_object(
            settings.minio_bucket,
            metadata_path,
            metadata_bytes,
            length=metadata_bytes.getbuffer().nbytes,
            content_type="application/json"
        )

        # Upload file
        file_bytes = BytesIO(file_data)
        minio_client.put_object(
            settings.minio_bucket,
            file_path,
            file_bytes,
            length=len(file_data),
            content_type="application/octet-stream"
        )

        print(f"Stored data for {device_name}/{sensor_name} at {time_path}")

    except Exception as e:
        print(f"Error processing MQTT message: {e}")
