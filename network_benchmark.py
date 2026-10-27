import time
import statistics
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import urlopen
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

WORKERS = 4
REPEATS = 3
URL_COUNT = 20
PORT = 8765


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        time.sleep(0.05)  # имитация задержки сети
        data = b"Hello from local server!\n"

        self.send_response(200)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format, *args):
        pass  # отключаем журнал запросов


def download(url):
    with urlopen(url, timeout=5) as response:
        return len(response.read())


def sequential(urls):
    return [download(url) for url in urls]


def threaded(urls):
    with ThreadPoolExecutor(max_workers=WORKERS) as executor:
        return list(executor.map(download, urls))


def multiprocess(urls):
    with ProcessPoolExecutor(max_workers=WORKERS) as executor:
        return list(executor.map(download, urls))


def benchmark(name, function, urls):
    times = []

    for run in range(1, REPEATS + 1):
        start = time.perf_counter()
        results = function(urls)
        elapsed = time.perf_counter() - start

        assert len(results) == URL_COUNT
        assert all(size > 0 for size in results)

        times.append(elapsed)
        print(f"{name}, запуск {run}: {elapsed:.3f} сек.")

    median = statistics.median(times)
    print(f"{name}, медиана: {median:.3f} сек.\n")
    return median


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    try:
        urls = [
            f"http://127.0.0.1:{PORT}/file/{i}"
            for i in range(URL_COUNT)
        ]

        time.sleep(0.1)
        print(f"URL: {URL_COUNT}; работников: {WORKERS}\n")

        results = {}
        results["Последовательно"] = benchmark(
            "Последовательно", sequential, urls
        )
        results["ThreadPoolExecutor"] = benchmark(
            "ThreadPoolExecutor", threaded, urls
        )
        results["ProcessPoolExecutor"] = benchmark(
            "ProcessPoolExecutor", multiprocess, urls
        )

        print("Сравнение медианного времени:")
        for name, elapsed in results.items():
            print(f"{name}: {elapsed:.3f} сек.")
    finally:
        server.shutdown()
        server.server_close()
