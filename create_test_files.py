import os
from gostcrypto import gosthash

def create_tests():
    print("=== Генератор тестовых файлов для ГОСТ Р 34.10-2012 ===")
    
    # Создаем обычный текстовый файл для подписания
    doc_name = "test_document.txt"
    doc_content = "Привет! Это тестовый секретный документ для проверки работы ЭЦП ГОСТ Р 34.10-2012."
    
    with open(doc_name, "w", encoding="utf-8") as f:
        f.write(doc_content)
    print(f"[+] Создан текстовый файл: {os.path.abspath(doc_name)}")
    
    print("\n[Успех] Все файлы готовы! Теперь вы можете:")
    print(f"1. Запустить основной скрипт, выбрать пункт 3 и сгенерировать ключи.")
    print(f"2. Выбрать пункт 1, указать путь к '{doc_name}' и подписать его.")
    print(f"3. Выбрать пункт 2 и проверить созданную подпись.")

if __name__ == "__main__":
    create_tests()
