import time
import msgpack
from app.startup_tasks import start_mqtt_listener, start_minio_client, exit_mqtt_listener


def test_end_to_end_integration(test_settings, minio_client, mqtt_client, mqtt_backend):
    # Replaced with mqtt_backend fixture
    # 1. Start Backend which is tested: MinIO and MQTT listener thread
    #test_minio_client = start_minio_client(settings=test_settings)
    #start_mqtt_listener(settings=test_settings, minio_client=test_minio_client)

    # Build msgpack payload
    payload = msgpack.packb({
        "metadata": {"type": "test", "value": 42},
        "file": b"fakebinarycontent"
    }, use_bin_type=True)

    topic = "/biofield-signal/deviceX/sensorY"

    # Publish the message
    mqtt_client.publish(topic, payload)
    mqtt_client.loop(2)  # Give it time to send

    # Wait for backend to process (tweak delay if needed)
    time.sleep(3)

    # Check in MinIO
    objects = list(minio_client.list_objects("test-bucket", prefix="deviceX/sensorY"))
    assert any("metadata.json" in obj.object_name for obj in objects)
    assert any("data.h5" in obj.object_name for obj in objects)

    # Replaced with mqtt_backend fixture
    #exit_mqtt_listener()
