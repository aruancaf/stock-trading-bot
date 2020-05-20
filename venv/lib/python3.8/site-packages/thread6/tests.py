import unittest
import time
import thread6


class TestThread6(unittest.TestCase):
    def setUp(self):
        pass

    def test_threaded_decorator(self):
        result = []

        @thread6.threaded(False)
        def append_x(arr):
            time.sleep(1)
            arr.append("x")
            return True

        # start the threaded function call
        a = append_x(result)
        result.append("y")
        # y should be appended first then x since main thread
        # is not waiting for x to finish
        self.assertEqual(result[0], "y")
        time.sleep(1)
        # x should now be appended
        self.assertEqual(len(result), 2)
        self.assertEqual(result[1], "x")
        # await_output should return function return
        self.assertTrue(a.await_output())

    def test_run_in_thread(self):
        # should do the same thing as the threaded decorator
        result = []

        def append_x(arr):
            time.sleep(1)
            arr.append("x")
            return True

        # start the threaded function call
        a = thread6.run_threaded(append_x, result)
        result.append("y")
        # y should be appended first then x since main thread
        # is not waiting for x to finish
        self.assertEqual(result[0], "y")
        time.sleep(1)
        # x should now be appended
        self.assertEqual(len(result), 2)
        self.assertEqual(result[1], "x")
        # await_output should return function return
        self.assertTrue(a.await_output())

    def test_run_chunked(self):
        results = []

        def append_nums(nums, arr):
            arr.extend(nums)

        manager = thread6.run_chunked(append_nums, range(10),
                                      threads=8, args=[results])
        self.assertEqual(len(results), 10)
        self.assertEqual(results, list(range(10)))
        # test manager methods
        self.assertEqual(len(manager.get_threads()), 10 % 8)
        # method smoke tests
        manager.start_all()
        manager.await_output()


if __name__ == '__main__':
    unittest.main()
