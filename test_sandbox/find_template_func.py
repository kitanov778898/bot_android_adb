"""
Песочница: функция поиска шаблона на изображении.
НАЗНАЧЕНИЕ:
Тестовая реализация find_template с полной обвязкой (таймер, логи, версия).
Используется для отладки поиска кнопок на скриншотах без реального ADB.
АВТОР: Виктор (с помощью ИИ)
ДАТА: 2026-10-05
СТАТУС: active
"""
import cv2
import logging
import time
from functools import wraps
from typing import Optional, Dict, Any, Tuple

# -----------------------------------------------------------------------------
# 1. ВЕРСИЯ МОДУЛЯ
# -----------------------------------------------------------------------------
__version__ = "1.0.2"

# -----------------------------------------------------------------------------
# 2. ЛОГИРОВАНИЕ
# -----------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("test_run.log", mode="a", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

# -----------------------------------------------------------------------------
# 3. ДЕКОРАТОР @timer
# -----------------------------------------------------------------------------
def timer(func):
    """Декоратор для замера времени выполнения функции."""
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
# 4. ОСНОВНАЯ ФУНКЦИЯ find_template
# -----------------------------------------------------------------------------
@timer
def find_template(
    screen_path: str,
    template_path: str,
    threshold: float = 0.85,
    roi: Optional[Tuple[int, int, int, int]] = None
) -> Optional[Dict[str, Any]]:
    """
    Ищет шаблон на изображении и возвращает координаты центра.
    
    :param screen_path: Путь к файлу скриншота (PNG/JPG).
    :param template_path: Путь к файлу шаблона (PNG/JPG).
    :param threshold: Порог уверенности совпадения (0.0 - 1.0).
    :param roi: Область поиска (x1, y1, x2, y2). Если None — ищем по всему экрану.
    :return: Словарь с результатом или None при критической ошибке.
    
    Формат при успехе:
        {"status": "success", "found": True, "cx": int, "cy": int, 
         "confidence": float, "message": str}
    
    Формат при отсутствии:
        {"status": "success", "found": False, "confidence": float, 
         "message": str}
    
    Формат при ошибке:
        {"status": "error", "message": str}
    
    .. versionadded:: 1.0.0
    """
    logging.info(f"🔍 Поиск шаблона: {template_path} на {screen_path}")
    logging.info(f"   Порог: {threshold}, ROI: {roi}")
    
    try:
        # Загружаем скриншот
        screen = cv2.imread(screen_path, cv2.IMREAD_COLOR)
        if screen is None:
            raise ValueError(f"Не удалось загрузить скриншот: {screen_path}")
        
        # Загружаем шаблон
        template = cv2.imread(template_path, cv2.IMREAD_COLOR)
        if template is None:
            raise ValueError(f"Не удалось загрузить шаблон: {template_path}")
        
        h, w = template.shape[:2]
        logging.info(f"   Шаблон загружен: {w}x{h} пикселей")
        
        # Определяем область поиска
        if roi is not None:
            x1, y1, x2, y2 = roi
            # Проверка границ
            if x1 < 0 or y1 < 0 or x2 > screen.shape[1] or y2 > screen.shape[0]:
                logging.warning(f"⚠️ ROI выходит за границы экрана! Экран: {screen.shape[1]}x{screen.shape[0]}")
            sub = screen[y1:y2, x1:x2]
        else:
            sub = screen
            x1, y1 = 0, 0
        
        # Защита: шаблон не должен быть больше области поиска
        if sub.shape[0] < h or sub.shape[1] < w:
            return {
                "status": "error",
                "message": f"Шаблон ({w}x{h}) больше области поиска ({sub.shape[1]}x{sub.shape[0]})"
            }
        
        # Поиск шаблона
        result = cv2.matchTemplate(sub, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        
        logging.info(f"   Максимальная уверенность: {max_val:.3f}")
        
        # Проверяем порог
        if max_val >= threshold:
            cx = max_loc[0] + w // 2 + x1
            cy = max_loc[1] + h // 2 + y1
            
            logging.info(f"✅ НАЙДЕНО! Координаты: ({cx}, {cy})")
            
            return {
                "status": "success",
                "found": True,
                "cx": cx,
                "cy": cy,
                "confidence": round(max_val, 3),
                "message": f"Шаблон найден в точке ({cx}, {cy}) с уверенностью {max_val:.3f}"
            }
        else:
            logging.info(f"❌ НЕ НАЙДЕНО (порог {threshold} > {max_val:.3f})")
            
            return {
                "status": "success",
                "found": False,
                "confidence": round(max_val, 3),
                "message": f"Шаблон не найден. Максимальная уверенность: {max_val:.3f}"
            }
    
    except Exception as e:
        logging.exception(f"Критическая ошибка при поиске шаблона: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

# -----------------------------------------------------------------------------
# 5. ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ: Визуализация результата
# -----------------------------------------------------------------------------
def visualize_result(
    screen_path: str,
    result: Dict[str, Any],
    roi: Optional[Tuple[int, int, int, int]] = None,
    output_path: str = "test_result.png"
):
    """
    Рисует ROI и найденную точку на скриншоте, сохраняет результат.
    
    :param screen_path: Путь к исходному скриншоту.
    :param result: Словарь с результатом find_template.
    :param roi: Область поиска для отрисовки.
    :param output_path: Путь для сохранения результата.
    """
    screen = cv2.imread(screen_path)
    if screen is None:
        logging.error(f"Не удалось загрузить {screen_path} для визуализации")
        return
    
    debug_img = screen.copy()
    
    # Рисуем ROI (зелёный прямоугольник)
    if roi is not None:
        x1, y1, x2, y2 = roi
        cv2.rectangle(debug_img, (x1, y1), (x2, y2), (0, 255, 0), 3)
        cv2.putText(debug_img, f"ROI: ({x1},{y1})-({x2},{y2})", 
                    (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 
                    0.8, (0, 255, 0), 2)
    
    # Рисуем найденную точку (красный круг)
    if result.get("found"):
        cx, cy = result["cx"], result["cy"]
        cv2.circle(debug_img, (cx, cy), 25, (0, 0, 255), -1)
        cv2.putText(debug_img, f"FOUND ({cx},{cy})", 
                    (cx + 30, cy), cv2.FONT_HERSHEY_SIMPLEX, 
                    1.0, (0, 0, 255), 2)
    
    cv2.imwrite(output_path, debug_img)
    logging.info(f"💡 Результат сохранён: {output_path}")

# -----------------------------------------------------------------------------
# 6. ТОЧКА ВХОДА ДЛЯ ТЕСТИРОВАНИЯ
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    # Тестовые данные
    SCREEN = "test_screen.png"
    TEMPLATE = "button_start.png"  # Скопируй из ../new/ или укажи свой путь
    #ROI = (1400, 50, 1900, 350)    # Из config.py
    ROI = None  # Ищем по всему экрану
    THRESHOLD = 0.75
    
    print("\n" + "=" * 60)
    print(f"🧪 ТЕСТ ФУНКЦИИ find_template")
    print(f"📦 Версия модуля: {__version__}")
    print("=" * 60 + "\n")
    
    # Вызов функции
    result = find_template(SCREEN, TEMPLATE, threshold=THRESHOLD, roi=ROI)
    
    # Обработка результата
    print("\n" + "=" * 60)
    if result and result.get("status") == "success":
        if result.get("found"):
            print(f"✅ УСПЕХ!")
            print(f"   Координаты: ({result['cx']}, {result['cy']})")
            print(f"   Уверенность: {result['confidence']}")
            print(f"   Время выполнения: {result['time_ms']} мс")
        else:
            print(f"❌ НЕ НАЙДЕНО")
            print(f"   Максимальная уверенность: {result['confidence']}")
            print(f"   Время выполнения: {result['time_ms']} мс")
    else:
        print(f"⚠️ ОШИБКА: {result}")
    print("=" * 60 + "\n")
    
    # Визуализация
    visualize_result(SCREEN, result, roi=ROI, output_path="test_result.png")