import threading


def run_chunked_threads(most_active_stocks, method, thread_count):
    partitioned_most_active_stock = partition_array(most_active_stocks, thread_count)
    threads = []

    for partition in partitioned_most_active_stock:
        threads.append(threading.Thread(target=method,
                                        args=[partition]))

    print("threadCount: {0}".format(len(threads)))

    for thread in threads:
        thread.start()

    threads[0].join()


def partition_array(arr, partition_count):
    k, m = divmod(len(arr), partition_count)
    return (arr[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(partition_count))


def run_thread(method):
    thread = threading.Thread(target=method)
    thread.start()
