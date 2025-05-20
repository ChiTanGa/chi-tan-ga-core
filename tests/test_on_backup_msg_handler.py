import time
import msgpack
import pytest
import threading

from minio import Minio
from paho.mqtt.client import Client as MqttClient

from app.mqtt import on_mqtt_backup_message_handler
from app.core import settings


@pytest.fixture(scope="module")
def minio_client_fixture():
    """Fixture to provide a connected MinIO client and clean up test data after."""
    ## TODO: The minio client needs to be spinned in the test configuration, for example different bucket name
    ## TODO: Original minio start can be extended for the test purpose
    minio_client = Minio(
        settings.minio_endpoint,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        secure=False
    )

    bucket = settings.minio_bucket
    if not minio_client.bucket_exists(bucket):
        minio_client.make_bucket(bucket)

    yield minio_client

    # Clean up all uploaded test objects
    for obj in minio_client.list_objects(bucket, recursive=True):
        minio_client.remove_object(bucket, obj.object_name)


def start_mqtt_listener_in_background(handler_func):
    """Starts an MQTT client that listens on the topic and invokes the handler."""

    def run_listener():
        mqtt_client = MqttClient()
        mqtt_client.on_message = lambda client, userdata, msg: handler_func(client, userdata, msg)
        mqtt_client.connect(settings.mqtt_host, settings.mqtt_port, 60)
        mqtt_client.subscribe("/biofield-signal-test/deviceA/sensorX")
        mqtt_client.loop_forever()

    thread = threading.Thread(target=run_listener, daemon=True)
    thread.start()
    time.sleep(3)  # Allow time for MQTT client to connect


def test_mqtt_backup_message(minio_client_fixture):
    """Integration test: send MQTT message and verify files are written to MinIO."""
    start_mqtt_listener_in_background(on_mqtt_backup_message_handler)

    # Prepare MQTT payload
    metadata = {"test": "value"}
    file_content = b"test_binary_data"
    payload = msgpack.packb({"metadata": metadata, "file": file_content})

    # Publish MQTT message
    mqtt_publisher = MqttClient()
    mqtt_publisher.connect(settings.mqtt_host, settings.mqtt_port)
    mqtt_publisher.publish("/biofield-signal-test/deviceA/sensorX", payload)
    mqtt_publisher.disconnect()

    # Allow time for processing
    time.sleep(3)

    # Check MinIO for the expected objects
    objects = list(minio_client_fixture.list_objects(
        settings.minio_bucket,
        prefix="deviceA/sensorX",
        recursive=True
    ))

    assert any(obj.object_name.endswith("metadata.json") for obj in objects), "Metadata file missing"
    assert any(obj.object_name.endswith("data.h5") for obj in objects), "Data file missing"
