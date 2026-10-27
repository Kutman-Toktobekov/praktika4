import os
import time
import statistics
from array import array
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

FILE = "numbers.txt"
WORKERS = 4
REPEATS = 3

# Загружаем числа один раз, до измерений.
# array хранит числа компактнее, чем обычный список Python.
with open(FILE, "r") as f:
    numbers = array("Q", (int(line) for line in f))

TOTAL = len(numbers)


def sum_range(bounds):
    start, end = bounds
    return sum(numbers[i] for i in range(start, end))


def make_chunks():
    chunk_size = (TOTAL + WORKERS - 1) // WORKERS
    return [
        (start, min(start + chunk_size, TOTAL))
        for start in range(0, TOTAL, chunk_size)
    ]


def sequential():
    return sum_range((0, TOTAL))


def threaded():
    with ThreadPoolExecutor(max_workers=WORKERS) as executor:
        return sum(executor.map(sum_range, make_chunks()))


def multiprocess():
    with ProcessPoolExecutor(max_workers=WORKERS) as executor:
        return sum(executor.map(sum_range, make_chunks()))


def benchmark(name, function):
    times = []
    result = None

    for run in range(1, REPEATS + 1):
        start = time.perf_counter()
        current_result = function()
        elapsed = time.perf_counter() - start

        if result is not None and current_result != result:
            raise ValueError("Результаты вычислений не совпадают!")

        result = current_result
        times.append(elapsed)
        print(f"{name}, запуск {run}: {elapsed:.3f} сек.")

    median = statistics.median(times)
    print(f"{name}, медиана: {median:.3f} сек.\n")
    return result, median


if __name__ == "__main__":
    print(f"Чисел: {TOTAL}")
    print(f"Процессоров доступно: {os.cpu_count()}")
    print(f"Потоков/процессов: {WORKERS}\n")

    results = {}

    for name, function in [
        ("Один поток", sequential),
        ("4 потока", threaded),
        ("4 процесса", multiprocess),
    ]:
        results[name] = benchmark(name, function)

    expected = sum(numbers)
    assert all(value[0] == expected for value in results.values())

    print("Итоговая сумма:", expected)
    print("\nСравнение медианного времени:")
    for name, (_, median) in results.items():
        print(f"{name}: {median:.3f} сек.")
