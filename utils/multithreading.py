import threading


def runChunkedThreads(most_active_stocks, method, thread_count):
    partitioned_most_active_stock = []
    for i in range(0, len(most_active_stocks), thread_count):
        partitioned_most_active_stock.append(most_active_stocks[i:i + thread_count])

    threads = []

    for partition in partitioned_most_active_stock:
        threads.append(threading.Thread(target=method,
                                        args=[partition]))

    for thread in threads:
        thread.start()

    threads[0].join()
