import threading
import multiprocessing


def change_list(shared_list):
    shared_list.append("изменено")


def thread_demo():
    data = ["начальное значение"]

    print("=== Потоки ===")
    print("До запуска потока:", data)

    thread = threading.Thread(target=change_list, args=(data,))
    thread.start()
    thread.join()

    print("После завершения потока:", data)


def process_demo():
    data = ["начальное значение"]

    print("\n=== Процессы ===")
    print("До запуска процесса:", data)

    process = multiprocessing.Process(target=change_list, args=(data,))
    process.start()
    process.join()

    print("После завершения процесса:", data)


if __name__ == "__main__":
    thread_demo()
    process_demo()
