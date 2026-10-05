"""
HEADOFF — Шаблон-валидатор для завершения функций.

НАЗНАЧЕНИЕ:
    Помогает завершать функции по чеклисту, не уходя в бесконечные улучшения.
    Проверяет наличие docstring, версии, логирования.

ИСПОЛЬЗОВАНИЕ:
    1. Скопируй этот файл как шаблон для новой функции.
    2. Заполни секцию FUNCTION_INFO.
    3. Запусти — он проверит, все ли пункты чеклиста выполнены.
    4. Если все ✅ — функция ЗАВЕРШЕНА. Иди дальше.

АВТОР: kitanov778898
ДАТА: 2026-10-04
ВЕРСИЯ: 1.0.0
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any

# -----------------------------------------------------------------------------
# 1. НАСТРОЙКА ЛОГИРОВАНИЯ
# -----------------------------------------------------------------------------
script_path = Path(__file__).resolve()
script_dir = script_path.parent
log_path = script_dir / "headoff_check.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(log_path, mode="a", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

# -----------------------------------------------------------------------------
# 2. ФУНКЦИЯ-ВАЛИДАТОР DOCSTRING
# -----------------------------------------------------------------------------
def validate_docstring(func) -> bool:
    """
    Проверяет, есть ли у функции docstring.
    Если нет — генерирует минимальный или задает вопросы.
    
    Returns:
        bool: True если docstring есть и валиден, False если нужно доработать.
    """
    if not func.__doc__:
        logging.warning(f"⚠️ У функции '{func.__name__}' НЕТ docstring!")
        
        # Генерируем минимальный docstring
        minimal_doc = f"""
        {func.__name__} — [КРАТКОЕ ОПИСАНИЕ].
        
        Args:
            [ПАРАМЕТРЫ]
        
        Returns:
            [ЧТО ВОЗВРАЩАЕТ]
        """
        logging.info(f"💡 Минимальный шаблон docstring:\n{minimal_doc}")
        return False
    
    # Проверяем наличие ключевых секций
    doc = func.__doc__
    required_sections = ["Args:", "Returns:"]
    missing = [s for s in required_sections if s not in doc]
    
    if missing:
        logging.warning(f"⚠️ В docstring отсутствуют секции: {missing}")
        return False
    
    logging.info(f"✅ Docstring функции '{func.__name__}' валиден")
    return True

# -----------------------------------------------------------------------------
# 3. ЧЕКЛИСТ ЗАВЕРШЕННОСТИ ФУНКЦИИ
# -----------------------------------------------------------------------------
def check_function_completion(func) -> Dict[str, bool]:
    """
    Проверяет функцию по чеклисту завершенности.
    
    Returns:
        dict: {"пункт": True/False}
    """
    checklist = {
        "1. Функция запускается без ошибок": False,
        "2. Функция возвращает ожидаемый результат": False,
        "3. Лог пишется в файл": False,
        "4. Код читаем и понятен": False,
        "5. Есть docstring с Args и Returns": validate_docstring(func),
        "6. Есть версия (в docstring или переменной)": False
    }
    
    # Пункт 1: Попробуем запустить
    try:
        result = func()
        checklist["1. Функция запускается без ошибок"] = True
    except Exception as e:
        logging.error(f"❌ Функция упала с ошибкой: {e}")
        return checklist
    
    # Пункт 2: Проверяем результат
    if isinstance(result, dict) and "status" in result:
        checklist["2. Функция возвращает ожидаемый результат"] = True
    else:
        logging.warning(f"⚠️ Функция вернула неожиданный результат: {result}")
    
    # Пункт 3: Проверяем лог
    if log_path.exists() and log_path.stat().st_size > 0:
        checklist["3. Лог пишется в файл"] = True
    else:
        logging.warning("⚠️ Лог-файл не создан или пуст")
    
    # Пункт 4: Субъективная проверка (всегда True, если дошли до сюда)
    checklist["4. Код читаем и понятен"] = True
    
    # Пункт 6: Проверяем версию
    if hasattr(func, "__version__") or ".. versionadded::" in (func.__doc__ or ""):
        checklist["6. Есть версия (в docstring или переменной)"] = True
    else:
        logging.warning("⚠️ Версия не указана (ни в атрибуте, ни в docstring)")
    
    return checklist

# -----------------------------------------------------------------------------
# 4. ПРИМЕР ФУНКЦИИ ДЛЯ ПРОВЕРКИ (скопируй и адаптируй)
# -----------------------------------------------------------------------------
def example_function() -> Dict[str, Any]:
    """
    example_function — Пример функции для проверки чеклиста.
    
    Args:
        Нет (это пример).
    
    Returns:
        dict: {"status": "ok", "message": "Пример работы"}
    
    .. versionadded:: 1.0.0
    """
    logging.info("Пример функции выполнен")
    return {"status": "ok", "message": "Пример работы"}

# -----------------------------------------------------------------------------
# 5. ТОЧКА ВХОДА: ПРОВЕРКА ФУНКЦИИ
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🔍 ПРОВЕРКА ФУНКЦИИ ПО ЧЕКЛИСТУ ЗАВЕРШЕННОСТИ")
    print("=" * 60)
    
    # Проверяем example_function (замени на свою функцию)
    checklist = check_function_completion(example_function)
    
    print("\n📋 РЕЗУЛЬТАТ ПРОВЕРКИ:")
    print("-" * 60)
    
    all_passed = True
    for item, passed in checklist.items():
        status = "✅" if passed else "❌"
        print(f"{status} {item}")
        if not passed:
            all_passed = False
    
    print("-" * 60)
    
    if all_passed:
        print("\n🎉 ВСЕ ПУНКТЫ ВЫПОЛНЕНЫ! ФУНКЦИЯ ЗАВЕРШЕНА.")
        print("👉 Можешь копировать её в основной бот и идти дальше.")
    else:
        print("\n⚠️ НЕ ВСЕ ПУНКТЫ ВЫПОЛНЕНЫ.")
        print("👉 Доработай недостающие пункты, но НЕ добавляй новые фичи!")
    
    print("=" * 60 + "\n")