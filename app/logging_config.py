import logging
from logging.handlers import RotatingFileHandler
import os

LOGS_DIR = "logs"
os.makedirs(LOGS_DIR, exist_ok=True)

def setup_logger():
    # Logger raíz para todo
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Archivo general
    regiodental_handler = RotatingFileHandler(
        os.path.join(LOGS_DIR, "regiodental.log"), maxBytes=5_000_000, backupCount=3
    )
    regiodental_handler.setFormatter(formatter)
    root_logger.addHandler(regiodental_handler)

    # Logger exclusivo para webhooks
    webhook_logger = logging.getLogger("webhook")
    webhook_logger.setLevel(logging.INFO)

    webhook_handler = RotatingFileHandler(
        os.path.join(LOGS_DIR, "webhook.log"), maxBytes=5_000_000, backupCount=3
    )
    webhook_handler.setFormatter(formatter)
    webhook_logger.addHandler(webhook_handler)

    # Opcional: evita que el logger 'webhook' duplique mensajes en root
    webhook_logger.propagate = False
