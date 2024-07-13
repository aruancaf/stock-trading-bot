"""Record elapsed time and number of function calls
"""

import sys
from time import time
from functools import total_ordering


@total_ordering
class _WhContextManager:

    def __init__(self, func, stream):
        self._args = self._kwds = self._ret = None
        self._func = func
        self._stream = stream
        self._started = self.ncall = self.elapsed = 0
        self._called = False

    def __call__(self, *args, **kwds):
        if self._called:
            return self._after_call(*args, **kwds)

        self._args = args
        self._kwds = kwds
        self._called = True
        return self

    def _after_call(self, *args, **kwds):
        self._record_start()
        self._ret = self._func(*args, **kwds)
        self._record_end()
        return self._ret

    def _record_start(self):
        self.ncall += 1
        self._started = time() * 1000

    def _record_end(self):
        self.elapsed += time() * 1000 - self._started

    def __enter__(self):
        self._record_start()
        self._ret = self._func(* self._args, ** self._kwds)
        self._record_end()
        return self._ret

    def reset(self):
        """Reset for another context"""
        self._called = False
        self.ncall = self.elapsed = 0

    def done(self):
        """Manually indicates task completion to trigger logging and reset"""
        self._stream.write(
            '[wh] {}: {} calls, {}(ms) elapsed\n'.format(
                self._func.__name__, self.ncall, self.elapsed
            )
        )
        self._stream.flush()
        self.reset()

    def __exit__(self, *_):
        self.done()

    def _check_call(self):
        if not self._called:
            raise TypeError('Function should be called at least once')

        self.__enter__()

    @property
    def retval(self):
        """Return value of the call"""
        self._check_call()
        return self._ret

    def __eq__(self, other):
        self._check_call()
        return self._ret == other

    def __lt__(self, other):
        self._check_call()
        return self._ret < other

    def __repr__(self):
        self._check_call()
        return repr(self._ret)

    def __str__(self):
        self._check_call()
        return str(self._ret)


def trek(stream=sys.stdout):
    """wh's decorator with context"""

    def _deco(func):
        return _WhContextManager(func, stream)

    return _deco
