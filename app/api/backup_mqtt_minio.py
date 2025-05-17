import logging
import msgpack
import json
from datetime import datetime
from minio import Minio
import paho.mqtt.client as mqtt
import paho.mqtt.enums as mqtt_enums
import threading
from io import BytesIO
from fastapi import APIRouter
from app.core import settings

logger = logging.getLogger(__name__)  # Use module-level logger

router = APIRouter()

# MinIO client
minio_client = Minio(
    settings.minio_endpoint,
    access_key=settings.minio_access_key,
    secret_key=settings.minio_secret_key,
    secure=False
)

bucket_name = "bio-field-data-backup"

# Ensure bucket exists
if not minio_client.bucket_exists(bucket_name):
    minio_client.make_bucket(bucket_name)


# MQTT handler
def on_message(client, userdata, msg):
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
            bucket_name,
            metadata_path,
            metadata_bytes,
            length=metadata_bytes.getbuffer().nbytes,
            content_type="application/json"
        )

        # Upload file
        file_bytes = BytesIO(file_data)
        minio_client.put_object(
            bucket_name,
            file_path,
            file_bytes,
            length=len(file_data),
            content_type="application/octet-stream"
        )

        print(f"Stored data for {device_name}/{sensor_name} at {time_path}")

    except Exception as e:
        print(f"Error processing MQTT message: {e}")


# MQTT setup
def mqtt_listener():
    client = mqtt.Client(callback_api_version=mqtt_enums.CallbackAPIVersion.VERSION2)
    client.on_message = on_message
    client.connect(settings.mqtt_host, settings.mqtt_port, 60)
    client.subscribe("/biofield-signal/+/+")

    client.loop_forever()


# Background MQTT thread
threading.Thread(target=mqtt_listener, daemon=True).start()


@router.get("/")
def health_check():
    return {"status": "running"}
