import hashlib
import itertools
import multiprocessing
import os
import time


def time_of_function(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print("Затраченное время:", execution_time, "сек.")
        return result

    return wrapper


def generate_passwords(repeat: int = 5) -> list[str]:
    letters = 'abcdefghijklmnopqrstuvwxyz'
    passwords = [''.join(i) for i in itertools.product(letters, repeat=repeat)]
    return passwords


def calculate_hash(string: str) -> str:
    sha256 = hashlib.sha256()
    sha256.update(string.encode('utf-8'))
    return sha256.hexdigest()


def check_string(string: str, hashes: list[str]) -> tuple[str, str] | None:
    decoded_string = calculate_hash(string)
    if decoded_string in hashes:
        return string, decoded_string
    else:
        return None


def input_hashes_from_keyboard() -> list[str] | None:
    print("После того, как введете хэши, отправьте пустую строку для продолжения")
    hashes = []
    while True:
        hash = input("Введите хэш: ")
        if hash == '':
            break
        else:
            hashes.append(hash)
    if len(hashes) == 0:
        return None
    return hashes


def input_hashes_from_file() -> list[str] | None:
    filename = input("Введите название файла с хешами: ")
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as file:
            data = file.read()
            hashes = data.split('\n')
            return hashes
    else:
        print("Файл не найден")
        return None


@time_of_function
def single_thread(hashes: list[str]):
    # 16.186832904815674 сек.
    all_password = generate_passwords()
    success_count = 0
    for password in all_password:
        result = check_string(password, hashes)
        if success_count == len(hashes):
            return
        if result is not None:
            success_count += 1
            print(f"Найдено соответствие: {result[1]} -> {result[0]}")


def worker(words, hashes):
    for word in words:
        result = check_string(word, hashes)
        if result is not None:
            print(f"Найдено соответствие: {result[1]} -> {result[0]}")


@time_of_function
def multi_thread(hashes: list[str], threads_count: int = 10):
    # 6.825169563293457 сек.
    all_password = generate_passwords()
    chunk_size = len(all_password) // threads_count
    threads = []
    chunks = []
    for i in range(threads_count):
        start = i * chunk_size
        end = start + chunk_size if i < threads_count - 1 else None
        chunk = all_password[start:end]
        chunks.append(chunk)
        thread = multiprocessing.Process(target=worker, args=(chunk, hashes))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()


if __name__ == '__main__':
    while True:
        input_type = input(
            "1. С клавиатуры\n"
            "2. Из файла\n"
            "Выберите тип ввода: "
        )
        if input_type == '1':
            hashes = input_hashes_from_keyboard()
            break
        elif input_type == '2':
            hashes = input_hashes_from_file()
            break
        else:
            print("Неверный ввод")
    threads_count = int(input("Введите кол-во потоков: "))
    # hashes = [
    #     "1115dd800feaacefdf481f1f9070374a2a81e27880f187396db67958b207cbad",
    #     "3a7bd3e2360a3d29eea436fcfb7e44c735d117c42d1c1835420b6b9942dd4f1b",
    #     "74e1bb62f8dabb8125a58852b63bdf6eaef667cb56ac7f7cdba6d7305c50a22f"
    # ]
    print(f"Введено {len(hashes)} хэшей")
    print("Перебор запущен!")
    if threads_count == 1:
        single_thread(hashes)
    elif threads_count > 1:
        multi_thread(hashes, threads_count)
