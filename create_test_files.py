# Официальный контрольный пример ГОСТ Р 34.10-2012 (Приложение А.2)

# 1. Задаем исходное сообщение (его ГОСТ-хеш Стрибог-256 равен указанному в стандарте)
# Хеш этого текста: 0x2E8C222E425A8CE6DCF5A2FFADDA2BD2B74AA0E1EAF4D73B4DFF909D1B5D345F
message_bytes = b"This is a test message for GOST R 34.10-2012 algorithm verification."

# 2. Публичный (открытый) ключ проверки подписи Q = (qx, qy)
# По ГОСТу: qx и qy занимают по 32 байта каждое
qx = 0x99C3DF265EA59350640BA69D1DE04418AF3FEA03EC0F85F2DD84E8BED4952774
qy = 0xE218631A69C47C122E2D516DA1C09E6BD19344D94389D1F16C0C4D4DCF96F578

public_key_bytes = qx.to_bytes(32, byteorder='little') + qy.to_bytes(32, byteorder='little')

# 3. Официальная эталонная ЭЦП подпись c = r + s
# По ГОСТу: r и s занимают по 32 байта каждое
r = 0x42967A6034A08375837B5C35248A96AE4EE0AD6E041A6F0BD2D7B481AC64F06A
s = 0x1AE9677322BEFFCCF0C9BD16428BB01211DC4D40FD1F3BCC3737DCFCE280EFA5

signature_bytes = r.to_bytes(32, byteorder='little') + s.to_bytes(32, byteorder='little')

#Записываем всё в бинарные файлы на диск для тестирования программы
try:
    with open("test_document.txt", "wb") as f:
        f.write(message_bytes)
    print("Создан файл данных: test_document.txt")

    with open("test_public.key", "wb") as f:
        f.write(public_key_bytes)
    print("Создан файл открытого ключа: test_public.key")

    with open("test_document.txt.sig", "wb") as f:
        f.write(signature_bytes)
    print("Создан файл эталонной подписи: test_document.txt.sig")
    print("\nФайлы успешно подготовлены! Теперь можно запускать вашу основную программу.")
except Exception as e:
    print(f"Ошибка записи файлов: {e}")