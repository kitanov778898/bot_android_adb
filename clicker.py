import time
try:
    i=0
    while True:
        i=i+1
        print(f"Клик №{i}")
        time.sleep(2)
except KeyboardInterrupt:
    print("\nСкрипт остановлен по  Ctrl+C")
finally:
    print(f"Остановлено. Всего кликов: {i}")
    print("конец.")
