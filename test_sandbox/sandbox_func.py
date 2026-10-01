import logging
from pathlib import Path

log_path = Path("test_run.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.FileHandler(log_path, mode="a", encoding="utf-8")]
)

logging.info("Запущен тестовый прогон")
