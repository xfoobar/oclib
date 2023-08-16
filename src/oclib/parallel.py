import multiprocessing as mp
import sys
from typing import Sequence, Callable,Self


class ParallelWorker:
    """
    This class is used to execute a sequence of workers in parallel.
    :parameter workers: a sequence of callables
    :parameter queue_size: the size of the queues, default=0 (unlimited)
    :parameter ignore_output: if True, the output queue will not be filled, default=False
    """

    def __init__(self, workers: Sequence[Callable], queue_size: int = 0, ignore_output: bool = False):
        self.__workers = workers
        self.__parallel = len(workers)
        self.__ignore_output = ignore_output
        self.input = mp.Queue(maxsize=queue_size)
        "input queue"
        self.output = mp.Queue(maxsize=queue_size)
        "output queue"
        self.errors = mp.Queue(maxsize=queue_size)
        "error queue"
        self.__processes: list[mp.Process] = []
        self.__input_finished = False

    def start(self):
        """
        start processes.
        :return:
        """
        if len(self.__processes) > 0:
            print('ParallelWorker.start() has already been called',file=sys.stderr)
            return
        for worker in self.__workers:
            p = mp.Process(target=ParallelWorker._execute,
                           args=(self.input,
                                 self.output,
                                 self.errors,
                                 worker, self.__ignore_output))
            self.__processes.append(p)
            p.start()

    def finish_input(self):
        """
        This method is used to signal the end of the input.
        :return:
        """
        if not self.__input_finished:
            for _ in range(self.__parallel):
                self.input.put(None)
            self.__input_finished = True

    def kill(self):
        """
        This method is used to kill all the processes.
        :return:
        """
        for p in self.__processes:
            if p.is_alive():
                p.terminate()

    @property
    def is_running(self):
        """
        This property is used to check if the processes are still running.
        :return:
        """
        for p in self.__processes:
            if p.is_alive():
                return True
        return False

    def wait(self):
        """
        This method is used to wait for all processes to finish.
        :return:
        """
        if not self.is_running:
            return
        for p in self.__processes:
            p.join()

    def get_results(self):
        """
        This method is used to get the results, it will wait for all processes to finish.
        :return:
        """
        self.wait()
        while not self.output.empty():
            yield self.output.get()

    @staticmethod
    def _execute(intput_queue: mp.Queue,
                 output_queue: mp.Queue,
                 error_queue: mp.Queue,
                 worker: Callable,
                 ignore_output: bool):
        """
        This method is used to execute a worker.
        :return:
        """
        for args in iter(intput_queue.get, None):
            try:
                r = worker(*args)
                if not ignore_output:
                    output_queue.put((args, r))
            except Exception as e:
                error_queue.put((args, e))
