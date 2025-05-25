import pytest
import socket
import time
from minio import Minio
import paho.mqtt.client as mqtt
import paho.mqtt.enums as mqtt_enums
from pytest_docker.plugin import Services
from app.core.config import Settings
from app.startup_tasks import start_mqtt_listener, exit_mqtt_listener, start_minio_client


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig):
    return [pytestconfig.rootpath / "docker-compose.yml", ]


@pytest.fixture(scope="session")
def test_settings():
    return Settings.from_env_file(env_file=".app-env.docker.test")


def wait_for_tcp(host: str, port: int, timeout: float = 30.0):
    """Wait until a TCP port is open."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=1):
                return
        except OSError:
            time.sleep(0.5)
    raise TimeoutError(f"Timed out waiting for {host}:{port}")


@pytest.fixture(scope="session")
def mqtt_client(docker_ip, test_settings):
    wait_for_tcp(docker_ip, test_settings.mqtt_port)

    client = mqtt.Client(callback_api_version=mqtt_enums.CallbackAPIVersion.VERSION2)
    client.connect(docker_ip, test_settings.mqtt_port)

    yield client

    client.disconnect()


def is_minio_responsive(host: str, port: int, access_key: str, secret_key: str) -> bool:
    """Checks if MinIO's S3 API is ready and accessible."""
    try:
        client = Minio(
            f"{host}:{port}",
            access_key=access_key,
            secret_key=secret_key,
            secure=False # Match your MinIO setup
        )
        # Attempt a simple API call to check readiness
        client.list_buckets()
        return True
    except Exception as e:
        print(f"MinIO not responsive at {host}:{port}: {e}") # Debugging
        return False

@pytest.fixture(scope="session")
def minio_client(docker_ip, docker_services: Services, test_settings):

    """
    Waits for the MinIO service to be responsive using a custom check,
    then returns its host IP and exposed port.
    """

    # Use wait_until_responsive with your custom check function
    docker_services.wait_until_responsive(
        timeout=30.0, # Total timeout for responsiveness
        pause=5.0,    # MinIO can take a bit longer to be ready, increased pause
        check=lambda: is_minio_responsive(
            docker_ip,
            test_settings.minio_port,
            test_settings.minio_access_key,
            test_settings.minio_secret_key
        )
    )

    client = Minio(
        f"{docker_ip}:{test_settings.minio_port}",
        access_key=test_settings.minio_access_key,
        secret_key=test_settings.minio_secret_key,
        secure=False
    )

    # Ensure test bucket exists
    if not client.bucket_exists(test_settings.minio_bucket):
        client.make_bucket(test_settings.minio_bucket)

    return client


# Real backend -> to be tested
@pytest.fixture(scope="session")
def mqtt_backend(test_settings: Settings):
    backend_minio_client = start_minio_client(settings=test_settings)
    start_mqtt_listener(settings=test_settings, minio_client=backend_minio_client)
    yield
    exit_mqtt_listener()
