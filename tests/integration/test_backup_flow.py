import time
import msgpack


def test_end_to_end_integration(test_settings, minio_client, mqtt_client, mqtt_backend):

    # Build msgpack payload
    payload = msgpack.packb({
        "metadata": {"type": "test", "value": 42},
        "file": b"fakebinarycontent"
    }, use_bin_type=True)

    topic = f"/{test_settings.mqtt_topic_root}/deviceX/sensorY"

    # Publish the message
    mqtt_client.publish(topic, payload)
    mqtt_client.loop(2)  # Give it time to send

    # Wait for backend to process (tweak delay if needed)
    time.sleep(3)

    # Check in MinIO
    objects = list(minio_client.list_objects(test_settings.minio_bucket, prefix="deviceX/sensorY/", recursive=True))
    assert any("metadata.json" in obj.object_name for obj in objects)
    assert any("data.h5" in obj.object_name for obj in objects)