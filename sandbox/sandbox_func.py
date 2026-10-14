"""
Песочница для отработки функций бота (ADB + Termux).

НАЗНАЧЕНИЕ:
    Тестовый mock-модуль. Имитирует ответы ADB, проверяет логирование,
    версионирование и структуру ответов без реального устройства.

ГДЕ ИСПОЛЬЗУЕТСЯ:
    - Termux: быстрая отладка новых функций.
    - Orange Pi: проверка запуска в урезанной среде.
    - Шаблон для создания других тестовых модулей.

АВТОР: kitanov778898
ДАТА: 2026-10-04
СТАТУС: active
"""

import logging
import time
from pathlib import Path
from functools import wraps
from typing import Dict, Any

# -----------------------------------------------------------------------------
# 1. ВЕРСИЯ МОДУЛЯ (MAJOR.MINOR.PATCH)
# -----------------------------------------------------------------------------
__version__ = "0.2.0"

# -----------------------------------------------------------------------------
# 2. ПУТИ И ЛОГИРОВАНИЕ
# -----------------------------------------------------------------------------
script_path = Path(__file__).resolve()
script_name = script_path.name
script_dir = script_path.parent
log_path = script_dir / "test_run.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(log_path, mode="a", encoding="utf-8"),
        logging.StreamHandler()  # Дублируем в консоль — так удобнее смотреть
    ]
)

logging.info(
    f"Запущен тестовый прогон: файл={script_name}, "
    f"путь={script_dir}, версия={__version__}"
)

# -----------------------------------------------------------------------------
# 3. ДЕКОРАТОР @timer (универсальный, можно копировать в основной бот)
# -----------------------------------------------------------------------------
def timer(func):
    """
    Декоратор для замера времени выполнения функции.
    Добавляет в возвращаемый словарь ключ 'time_ms', если функция вернула dict.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed_ms = (time.perf_counter() - start) * 1000

        if isinstance(result, dict):
            result["time_ms"] = round(elapsed_ms, 2)

        logging.info(f"⏱ '{func.__name__}' отработала за {elapsed_ms:.2f} мс")
        return result
    return wrapper

# -----------------------------------------------------------------------------
# 4. ТЕСТОВАЯ ФУНКЦИЯ (mock ADB-пинга)
# -----------------------------------------------------------------------------
@timer
def test_adb_ping() -> Dict[str, Any]:
    """
    Тестовый «пинг» ADB-соединения (mock-функция).

    Не делает реального запроса к устройству — служит заглушкой для проверки:
    что логи пишутся, версия видна, декоратор @timer работает.

    Returns:
        dict: {"status": "ok", "test": "adb_ping", "time_ms": float}
    """
    logging.info("Тестовый ADB-пинг выполнен")
    return {"status": "ok", "test": "adb_ping"}

# -----------------------------------------------------------------------------
# 5. ТОЧКА ВХОДА
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    result = test_adb_ping()

    print("\n" + "=" * 50)
    print(f"📦 Файл:       {script_name}")
    print(f"🔖 Версия:     {__version__}")
    print(f"📂 Путь:       {script_dir}")
    print(f"📝 Лог:        {log_path}")
    print("=" * 50)
    print(f"✅ Результат:  {result}")
    print("=" * 50 + "\n")
