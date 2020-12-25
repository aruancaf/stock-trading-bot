# this file simplifies multithreading
import threading


class ResultThread(threading.Thread):
    """
    A custom Thread that can return the value of the function 
    runned inside it
    """
    fx_output = None

    def run(self, *args, **kwargs):
        try:
            if self._target:
                self.fx_output = self._target(*self._args, **self._kwargs)
        finally:
            # Avoid a refcycle if the thread is running a function with
            # an argument that has a member that points to the thread.
            del self._target, self._args, self._kwargs

    def await_output(self):
        """
        Wait for the thread to finish and return the return value of fx
        """
        self.join()
        return self.fx_output


class MultiThreadManager(object):
    """
    A manager to manage the execution of multiple threads. Provide
    method to return a list of return values
    """
    threads = []

    def __init__(self, threads=[]):
        """
        Initialise a MultiThreadManager

        :param threads: a list of ResultThread objects
        :return: None
        """
        self.threads = threads

    def add_thread(self, thread):
        """
        Add a thread for this manager to manage

        :param thread: a ResultThread object
        :return: None
        """
        self.threads.append(thread)

    def get_threads(self):
        """
        Return a list of threads this manager is managing

        :return: list of ResultThread objects
        """
        return self.threads

    def start_all(self):
        """
        Attempt to start all threads. This will ignore the RunTimeError
        raised when Thread.start() is called multiple time
        """
        for t in self.threads:
            try:
                t.start()
            except RuntimeError:
                pass

    def await_output(self):
        """
        Wait for all threads to finish executing and return a list
        of all return values

        :return: list of objects
        """
        results = []
        for t in self.threads:
            results.append(t.await_output())
        return results


def threaded(daemon=False):
    """
    A decorator to run a function in a separate thread, this is useful
    when you want to do any IO operations (network request, prints, etc...)
    and want to do something else while waiting for it to finish.

    :param fx: the function to run in a separate thread
    :param daemon: boolean whether or not to run as a daemon thread
    :return: whatever fx returns
    """
    def _threaded(fx):
        def wrapper(*args, **kwargs):
            thread = ResultThread(target=fx, daemon=daemon,
                                  args=args, kwargs=kwargs)
            thread.start()
            return thread
        return wrapper

    return _threaded


@threaded(False)
def run_threaded(fx, *args, **kwargs):
    """
    Helper function to run a function in a separate thread

    :param fx: the function to run in a separate thread
    :param args: list arguments to pass to fx
    :param kwargs: dictionary keyword arguments to pass to fx
    :return: whatever fx returns
    """
    return fx(*args, **kwargs)


def run_chunked(fx, dataset, threads=8, args=(), kwargs={}):
    """
    Given an list of data, split it into smaller chunks
    and feed it to the processing function(fx) to be runned
    in separate threads. fx must take arguments in the format:

    fx(list, *args, **kwargs)

    :param fx: the processing function to run
    :param dataset: list to split
    :param threads: int how many threads to use when splitting
                    the dataset and running the function
    :param args: list of arguments to pass to fx
    :param kwargs: dictionary of keyword arguments to pass to fx
    :return: an instance of _pp.MultiThreadManager
    """
    # number of chunks <= number of threads
    chunks = []
    for i in range(0, len(dataset), threads):
        chunks.append(dataset[i:i + threads])
    manager = MultiThreadManager()
    for chunk in chunks:
        manager.add_thread(run_threaded(fx, chunk, *args, **kwargs))

    return manager
