# filepath: fastapi-leave-service/app/publisher.py
import json
import os
from pathlib import Path
from typing import Dict, Any
from app.config import settings

try:
    from google.cloud import pubsub_v1
except Exception:
    pubsub_v1 = None


class NoopPublisher:
    def publish_leave_approved(self, payload: Dict[str, Any]):
        print("[EVENT:NOOP] leave_approved:", json.dumps(payload))


class PubSubPublisher:
    def __init__(self, topic: str):
        if pubsub_v1 is None:
            raise RuntimeError("google-cloud-pubsub not installed")
        # PublisherClient will use ADC (GOOGLE_APPLICATION_CREDENTIALS or other ADC)
        self.topic = topic
        self.client = pubsub_v1.PublisherClient()

    def publish_leave_approved(self, payload: Dict[str, Any]):
        data = json.dumps(payload).encode("utf-8")
        future = self.client.publish(self.topic, data)
        return future.result()


def get_publisher():
    """
    Intenta crear un PubSubPublisher sólo si hay topic configurado.
    Si falta configuración o fallan las credenciales, devuelve NoopPublisher.
    """
    if not settings.pubsub_topic:
        print("[INFO] PUBSUB_TOPIC no configurado -> usando NoopPublisher")
        return NoopPublisher()

    if pubsub_v1 is None:
        print("[WARN] google-cloud-pubsub no instalado -> usando NoopPublisher")
        return NoopPublisher()

    # Preferimos comprobar GOOGLE_APPLICATION_CREDENTIALS para dar un mensaje claro, pero
    # también aceptamos ADC configurado de otra forma (gcloud auth application-default login, metadata service, etc).
    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if cred_path:
        p = Path(cred_path)
        if not p.exists():
            print(f"[WARN] GOOGLE_APPLICATION_CREDENTIALS='{cred_path}' no encontrado -> intentando inicializar, puede fallar")
    try:
        return PubSubPublisher(settings.pubsub_topic)
    except Exception as e:
        print(f"[WARN] PubSubPublisher inicialización falló: {e}. Usando NoopPublisher")
        return NoopPublisher()


# instancia compartida (lazy-safe)
publisher = get_publisher()