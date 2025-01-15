import logging
import os

# create logs dir
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    filename="logs/annotationTranslator.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

def get_logger(name : str):
    return logging.getLogger(name)
