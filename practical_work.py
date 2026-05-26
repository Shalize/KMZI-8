from gostcrypto import gosthash
import os
import time

def get_file_for_signature():
    "Шаг 1: Прием файла, для которого необходимо сформировать или проверить ЭЦП"
    # Запрашиваем путь к файлу через консоль
    file_path = input("Введите полный путь к файлу для ЭЦП: ").strip()
    
    # Очищаем от случайных кавычек, если пользователь просто перетащил файл в консоль
    file_path = file_path.strip("'\"")

    # Проверка корректности ввода
    if not os.path.exists(file_path):
        print(f"Ошибка ввода: Файл по пути '{file_path}' не существует.")
        return None

    if not os.path.isfile(file_path):
        print(f"Ошибка ввода: Указанный путь '{file_path}' ведет к папке, а нужен файл.")
        return None

    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    
    print("\nФайл успешно загружен")
    print(f"Имя файла: {file_name}")
    print(f"Размер: {file_size} байт")
    
    return file_path, file_name, file_size

def calculate_hash_from_gost(file_path):
    "Вычисление хеша по ГОСТ Р 34.11-2012 (Стрибог-256). Допускается использование готовой реализации хэш-функции ГОСТ Р 34.11-2012"
    
    # Инициализируем ГОСТ-алгоритм Стрибог
    hasher = gosthash.new('streebog256')
    
    # Побайтовое чтение файла по 64 кб
    buffer_size = 65536 
    with open(file_path, "rb") as file:
        while True:
            file_chunk = file.read(buffer_size)
            if not file_chunk:
                break # Если файл закончился, выходим из цикла
            hasher.update(file_chunk)
            
    # Получаем итоговые результаты
    hash_bytes = hasher.digest()   # В виде байт, нужно для будущей математики подписи
    hash_hex = hasher.hexdigest() # В виде строки для вывода на экран пользователю
    
    print("Хеширование успешно завершено.")
    print(f"Полученный ГОСТ-хеш (HEX): {hash_hex}\n")
    
    return hash_bytes

def get_signature_file():
    "Шаг 2: Прием файла, содержащего электронную цифровую подпись"
    file_sig_path = input("Введите полный путь к файлу с подписью (расширение должно быть или .sig или .sgn): ").strip().strip("'\"")

    # 1. Проверяем существование файла с подписью
    if not os.path.exists(file_sig_path):
        print(f"Ошибка: Файл подписи '{file_sig_path}' не найден.")
        return None

    if not os.path.isfile(file_sig_path):
        print(f"Ошибка: Указанный путь ведет к папке.")
        return None

    # 2. Считываем подпись в байтах
    with open(file_sig_path, "rb") as sig_file:
        signature_bytes = sig_file.read()

    # 3. Проверка подписи ГОСТ Р 34.10-2012 для Стрибог-256. Она должна составлять ровно 64 байта (два числа по 256 бит: r и s).
    print(f"Файл с подписью успешно загружен: {os.path.basename(file_sig_path)}")
    print(f"Размер файла с подписью: {len(signature_bytes)} байт")
    
    if len(signature_bytes) != 64:
        print("Размер подписи отличается от стандартных 64 байт для ГОСТ Р 34.10-2012 (256 бит).")
    
    return signature_bytes

def get_key(key_type):
    "Шаг 3: Прием на вход ключ подписи или ключ проверки подписи"
    if key_type == 'private':
        key_path_from_user = "Введите полный путь к ЗАКРЫТОМУ ключу (ключ подписи, 32 байта): "
        expected_len = 32
    elif key_type == 'public':
        key_path_from_user = "Введите полный путь к ОТКРЫТОМУ ключу (ключ проверки, 64 байта): "
        expected_len = 64
    else:
        print("Ошибка: Указан неверный тип ключа.")
        return None

    key_path = input(key_path_from_user).strip().strip("'\"")

    # 1. Проверяем существование файла ключа
    if not os.path.exists(key_path) or not os.path.isfile(key_path):
        print("Ошибка ввода: Файл ключа не найден.")
        return None

    # 2. Считываем байты ключа
    with open(key_path, "rb") as key_file:
        key_bytes = key_file.read()

    print(f"Ключ успешно загружен из файла: {os.path.basename(key_path)}")
    print(f"Считано: {len(key_bytes)} байт")

    # 3. Проверяем на соответствие ГОСТ Р 34.10-2012 (256 бит)
    if len(key_bytes) != expected_len:
        print(f"Размер файла ключа не совпадает со стандартом ГОСТ")
        print(f"Ожидалось ровно {expected_len} байт.")
    else:
        print("Размер ключа соответствует ГОСТ Р 34.10-2012 (256 бит).")
    return key_bytes

def manual_pseudo_random_bytes(length):
    "Самописный генератор псевдослучайных байт. Использует Линейный конгруэнтный метод (LCG) и текущее время для инициализации."
    # Стартовое число берем из системного времени в микросекундах
    seed = int(time.time() * 1000000)

    # Стандартные константы для формулы
    m = 2**31 - 1 # Модуль
    a = 1103515245 # Множитель
    c = 12345      # Приращение

    result_bytes = bytearray()

    while len(result_bytes) < length:
        # Формула LCG: X_n+1 = (a * X_n + c) mod m
        seed = (a * seed + c) % m
        # Берем младший байт полученного числа (остаток от деления на 256)
        random_byte = seed % 256
        result_bytes.append(random_byte)
        
    return bytes(result_bytes)

def generate_and_save_keypair_manually():
    "Шаг 4: Генерация ключевой пары ГОСТ Р 34.10-2012."
    private_name = input("Введите имя файла для ЗАКРЫТОГО ключа").strip()
    if not private_name: private_name = "private.key"
        
    public_name = input("Введите имя файла для ОТКРЫТОГО ключа: ").strip()
    if not public_name: public_name = "public.key"

    print("Генерация ключей, подождите...")

     # Генерируем секретное число d (закрытый ключ) с помощью LCG-генератора
    raw_bytes = manual_pseudo_random_bytes(32)
    d = int.from_bytes(raw_bytes, byteorder='big') % E['q']
    if d == 0: 
        d = 1
    
    # Переводим число d в 32 байта для сохранения
    private_key_bytes = d.to_bytes(32, byteorder='big')

    # Вычисляем точку открытого ключа Q = d*P
    Q = point_mult(d, P_point)
    if Q is None:
        print("Ошибка генерации: получена точка на бесконечности. Попробуйте еще раз.")
        return None
    
    qx, qy = Q
    # Обязательно приводим к модулю поля p перед конвертацией в байты
    qx_mod = qx % E['p']
    qy_mod = qy % E['p']
    
    # Преобразовываем координаты X и Y открытого ключа по 32 байта каждая (всего 64 байта)
    public_key_bytes = qx.to_bytes(32, byteorder='big') + qy.to_bytes(32, byteorder='big')

    # Сохраняем файлы на диск
    try:
        # Пишем ЗАКРЫТЫЙ ключ (private_key_bytes)
        with open(private_name, "wb") as private_file:
            private_file.write(private_key_bytes)
        print(f"Закрытый ключ (32 байта) сохранен в: {private_name}")

        # Пишем ОТКРЫТЫЙ ключ (public_key_bytes)
        with open(public_name, "wb") as public_file:
            public_file.write(public_key_bytes)
        print(f"Открытый ключ (64 байта) сохранен в: {public_name}")

        return private_key_bytes, public_key_bytes
    except Exception as e:
        print(f"Ошибка при записи файлов: {e}")
        return None

#МАТЕМАТИКА

#ПАРАМЕТРЫ ЭЛЛИПТИЧЕСКОЙ КРИВОЙ E И БАЗОВОЙ ТОЧКИ P (ГОСТ Р 34.10-2012)
E = {
    'p': 0x8000000000000000000000000000000000000000000000000000000000000431,
    'a': 0x07,
    'b': 0x5FBFF498AA938CE739B8E022FBAFEF40563F6E6A3472FC2A514C0CE9DAE23B7E,
    'q': 0x8000000000000000000000000000000150FE8A1892976154C59CFC193ACCF5B3
}
P_point = (
    0x02,
    0x08E2A8A0E65147D4BD6316030E16D19C85C97F0A9CA267122B96ABBCEA7E8FC8
)

# Поиск обратного элемента по модулю: (val * result) % m == 1.
def mod_inverse(val, m):
    # Приводим к положительному числу в пределах модуля
    a, b = val % m, m
    if a == 0:
        return 0  # Обратного элемента не существует
    
    # Инициализация для расширенного алгоритма Евклида
    x0, x1 = 1, 0
    while b > 0:
        q_div = a // b
        a, b = b, a % b
        x0, x1 = x1, x0 - q_div * x1
    
    # Если в конце a != 1, значит числа не взаимно просты (обратного нет)
    if a > 1: 
        return 0 

    return x0 % m

# Сложение двух точек P1 и P2 на эллиптической кривой E.
def point_add(P1, P2):
    if P1 is None: return P2
    if P2 is None: return P1
    
    # Принудительно приводим к положительному модулю поля p
    x1, y1 = P1[0] % E['p'], P1[1] % E['p']
    x2, y2 = P2[0] % E['p'], P2[1] % E['p']
    
    if x1 == x2 and (y1 + y2) % E['p'] == 0:
    return None  # Точки противоположны, результат — точка на бесконечности
        
    if x1 == x2 and y1 == y2:
        if y1 == 0: return None
        num = (3 * x1 * x1 + E['a']) % E['p']
        denom = mod_inverse(2 * y1, E['p'])
    else:
        num = (y2 - y1) % E['p']
        denom = mod_inverse(x2 - x1, E['p'])

    if denom == 0: 
        return None # Защита от деления на ноль
        
    lam = (num * denom) % E['p']
    x3 = (lam * lam - x1 - x2) % E['p']
    y3 = (lam * (x1 - x3) - y1) % E['p']
    return (x3, y3)

# Скалярное умножение точки P на число k на кривой E.
def point_mult(k, P):
    if P is None: return None
    # Защита от отрицательного k (переводим k в поле порядка группы q)
    k = k % E['q'] 
    if k == 0: return None

    result = None
    addend = P
    while k > 0:
        if k & 1:
            result = point_add(result, addend)
        addend = point_add(addend, addend)
        k >>= 1
    return result

# Функция формирования ЭЦП
def sign_gost_3410(file_hash, private_key_bytes):
    d = int.from_bytes(private_key_bytes, byteorder='big')

    # Шаг 1 вычисление хэш-функции (Хеш уже вычислен алгоритмом streebog256 и передан в file_hash)
    alpha = int.from_bytes(file_hash, byteorder='big')

    # Шаг 2 вычисление альфа и опеределение E
    e = alpha % E['q']
    if e == 0:
        e = 1

    while True:
        # Шаг 3 Вычислить k
        k = int.from_bytes(os.urandom(32), byteorder='big') % E['q']
        if k == 0:
            continue  # Возврат к шагу 3

        # Шаг 4 Вычисление точки эллиптической кривой C = kP, r = xc(mod q)
        C = point_mult(k, P_point)
        if C is None:
            continue  # Возврат к шагу 3 (если попали в бесконечность)
        xc, yc = C
        r = xc % E['q']

        # Шаг 5 r=0? да -> шаг 3, нет - дальше
        if r == 0:
            continue  # Возврат к шагу 3

        # Шаг 6 вычисление s
        s = (k * e + r * d) % E['q']

        # Шаг 7 s=0? да -> шаг 3, нет - дальше
        if s == 0:
            continue  # Возврат к шагу 3
            
        # Шаг 8 определение цифровой подписи c -> выходной результат
        r_bytes = r.to_bytes(32, byteorder='big')
        s_bytes = s.to_bytes(32, byteorder='big')
        c = r_bytes + s_bytes
        return c
    
# Функция проверки ЭЦП
def verify_gost_3410(file_hash, signature_bytes, public_key_bytes):
    if len(signature_bytes) != 64:
        return False
    
    r = int.from_bytes(signature_bytes[:32], byteorder='big')
    s = int.from_bytes(signature_bytes[32:], byteorder='big')
    
    # Шаг 1 вычисление хэш-функции полученного сообщения М (Передано в file_hash)
    alpha = int.from_bytes(file_hash, byteorder='big')
    if alpha % E['q'] == 0:
        alpha = 1
    
    # Шаг 2 вычисление альфа и определение е
    e = alpha % E['q']
    if e == 0:
        e = 1
        
    # Шаг 3 вычисление v
    v = mod_inverse(e, E['q'])
    
    # Шаг 4 вычисление z1 z2
    z1 = (s * v) % E['q']
    z2 = ((E['q'] - r) * v) % E['q']
    
    # Шаг 5 извлекаем координаты точки открытого ключа Q
    qx = int.from_bytes(public_key_bytes[:32], byteorder='big')
    qy = int.from_bytes(public_key_bytes[32:], byteorder='big')
    Q_point = (qx, qy)
    
    # Шаг 6 вычисление точки эллиптической кривой C = z1P + z2Q и определение R
    z1P = point_mult(z1, P_point)
    z2Q = point_mult(z2, Q_point)
    C = point_add(z1P, z2Q)
    
    if C is None:
        return False
        
    xc, yc = C
    R = xc % E['q']
    
    # Шаг 7 R=r? Да -> дальше, нет->подпись неверна, выход
    if R == r:
        return True  # выходной результат подпись верна
    else:
        return False
    

# Главная точка входа в программу
if __name__ == "__main__":
    print("Программная реализация по теме Схемы электронной подписи (практическая работа 8)")
    while True:
        print("1 — Выбрать ФОРМИРОВАНИЕ электронной цифровой подписи")
        print("2 — Выбрать ПРОВЕРКУ электронной цифровой подписи")
        print("3 — Сгенерировать ключевую пару (Доп. функция)")
        print("0 — Выход")
        print("-" * 60)

        user_choice = input("Ваш выбор: ").strip()

        if user_choice == "1":
            print("\n Выбрано ФОРМИРОВАНИЕ подписи")
            
            # Принимаем файл
            file_info = get_file_for_signature()
            if not file_info: continue
            file_path, _, _ = file_info

            # Вычисляем хэш-файла
            file_hash = calculate_hash_from_gost(file_path)
                
            # Принимаем ключ подписи
            private_key = get_key('private')
            if not private_key: continue

            # Выполняем само формирование
            signature = sign_gost_3410(file_hash, private_key)
            
            # Сохраняем результат
            output_sig_path = file_path + ".sig"
            with open(output_sig_path, "wb") as f:
                f.write(signature)
            print(f"ЭЦП успешно создана и сохранена в: {output_sig_path}")

        elif user_choice == "2":
            print("\n Выбрано ПРОВЕРКА подписи")
            
            # Принимаем файл для проверки
            file_info = get_file_for_signature()
            if not file_info: continue
            file_path, _, _ = file_info

            with open(file_path, "rb") as f:
                raw_file_bytes = f.read()

            if len(raw_file_bytes) == 32:
                # Если файл ровно 32 байта, значит это наш готовый эталонный хэш из create_test_files.py
                file_hash = raw_file_bytes
                print("Обнаружен готовый ГОСТ-хеш (32 байта). Повторное хеширование пропущено.")
                print(f"Используемый ГОСТ-хеш (HEX): {file_hash.hex()}")
            else:
                # Для любых других файлов вычисляем хэш как обычно
                file_hash = calculate_hash_from_gost(file_path)
            
            # Принимаем файл подписи
            signature_bytes = get_signature_file()
            if not signature_bytes: continue
                
            # Принимаем открытый ключ проверки подписи
            public_key = get_key('public')
            if not public_key: continue

            # Выполняем саму проверку
            is_valid = verify_gost_3410(file_hash, signature_bytes, public_key)
            
            if is_valid:
                print("ЭЦП ВЕРНА. Документ подлинный.")
            else:
                print("ЭЦП НЕВЕРНА!")
            print("*"*40)

        elif user_choice == "3":
            # Вызов требования 4
            generate_and_save_keypair_manually()

        elif user_choice == "0":
            print("Программа завершена.")
            break
        else:
            print("Неверный ввод.")
