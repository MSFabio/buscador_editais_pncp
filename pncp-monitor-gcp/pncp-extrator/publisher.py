"""
Publica lotes de editais transformados no Google Cloud Pub/Sub.
Cada mensagem contém um array JSON de até 50 editais leves.
"""

import json
import logging
import os

logger = logging.getLogger(__name__)

BATCH_SIZE = 50


class EditalPublisher:
    """Wrapper para publicação de mensagens no Pub/Sub."""

    def __init__(self, project_id: str):
        from google.cloud import pubsub_v1
        self.client = pubsub_v1.PublisherClient()
        self.topic = f"projects/{project_id}/topics/pncp-editais-brutos"

    def publicar_lote(self, editais: list[dict]) -> int:
        """
        Publica um lote de editais como uma única mensagem Pub/Sub.
        Retorna o número de editais publicados.
        """
        if not editais:
            return 0

        payload = json.dumps(editais, ensure_ascii=False).encode("utf-8")
        future = self.client.publish(self.topic, data=payload)
        message_id = future.result()

        logger.info(
            f"Lote de {len(editais)} editais publicado | "
            f"message_id={message_id} | bytes={len(payload)}"
        )
        return len(editais)


class LocalPublisher:
    """
    Publisher local que salva os lotes em arquivo JSON.
    Usado para desenvolvimento e testes sem GCP.
    """

    def __init__(self, output_dir: str = "./output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self._counter = 0

    def publicar_lote(self, editais: list[dict]) -> int:
        if not editais:
            return 0

        self._counter += 1
        filepath = os.path.join(self.output_dir, f"lote_{self._counter:04d}.json")

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(editais, f, indent=2, ensure_ascii=False)

        logger.info(f"Lote de {len(editais)} editais salvo em {filepath}")
        return len(editais)
