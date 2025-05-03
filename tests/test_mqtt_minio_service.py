import time
import msgpack
import json
from io import BytesIO
from datetime import datetime

import pytest
from minio import Minio
import paho.mqtt.publish as publish

# Configuration
MQTT_HOST = "localhost"
MQTT_PORT = 1883
TOPIC = "/biofield-signal/test-device/test-sensor"
MINIO_HOST = "localhost:9000"
MINIO_BUCKET = "bio-field-data-backup"
MINIO_ACCESS_KEY = "OsJDYfZMJJMzfXCVidK7"
MINIO_SECRET_KEY = "NNAqnWs8jv8M4WODGsrHoIrhZNtW4jZy0acncIQt"

# Message content
metadata = {
    "sensor_id": "integration-test-sensor",
    "timestamp": datetime.utcnow().isoformat()
}
file_bytes = b"fake_h5_data"

@pytest.mark.integration
def test_mqtt_to_minio_pipeline():
    # Pack message using MessagePack
    payload = {
        "metadata": metadata,
        "file": file_bytes
    }
    packed = msgpack.packb(payload, use_bin_type=True)

    # Publish the message
    publish.single(
        TOPIC,
        payload=packed,
        hostname=MQTT_HOST,
        port=MQTT_PORT,
    )

    # Wait for backend to process
    time.sleep(2)  # give FastAPI listener time to process

    # Build expected path
    now = datetime.utcnow()
    folder_path = now.strftime("test-device/test-sensor/%Y/%m/%d/%H-%M")

    minio_client = Minio(
        MINIO_HOST,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False
    )

    # Check metadata.json
    metadata_path = f"{folder_path}/metadata.json"
    response = minio_client.get_object(MINIO_BUCKET, metadata_path)
    fetched_metadata = json.load(response)
    assert fetched_metadata["sensor_id"] == metadata["sensor_id"]

    # Check .h5 file
    file_path = f"{folder_path}/data.h5"
    file_obj = minio_client.get_object(MINIO_BUCKET, file_path)
    fetched_file_data = file_obj.read()
    assert fetched_file_data == file_bytes
