import time
import logging
import asyncio

from functools import wraps

logger = logging.getLogger(__file__.split("/")[-1])


__LIMIT_TIMEIT_PRINT_MAX_LEN__ = 128


def timeit(
    func=None,
    *,
    __level: int = logging.DEBUG,
    __output_args: bool = False,
    __output_maxlen: int = __LIMIT_TIMEIT_PRINT_MAX_LEN__,
):
    if func is not None:
        return timeit(__level=__level, __output_args=__output_args, __output_maxlen=__output_maxlen)(func)

    def _get_timeit_arg_print(*args, **kwargs):
        args_print = f"{args}"
        args_print = args_print if len(args_print) < __output_maxlen else args_print[: __output_maxlen - 4] + "...)"
        kwargs_print = f"{kwargs}"
        kwargs_print = kwargs_print if len(kwargs_print) < __output_maxlen else kwargs_print[: __output_maxlen - 4] + "...}"
        return args_print, kwargs_print

    def _decorator(func):
        if logger.level > __level:
            return func
        is_async = asyncio.iscoroutinefunction(func)

        @wraps(func)
        async def _async_timeit_wrapper(*args, **kwargs):
            if __output_args:
                args_print, kwargs_print = _get_timeit_arg_print(args, kwargs)
                logger.log(__level, f"async call {func.__name__} {args_print} {kwargs_print}")
            else:
                logger.log(__level, f"async call {func.__name__}")
            start_time = time.perf_counter()
            result = await func(*args, **kwargs)
            end_time = time.perf_counter()
            total_time = end_time - start_time
            logger.log(__level, f"async quit {func.__name__} Took {total_time:.3f} seconds")
            return result

        @wraps(func)
        def _sync_timeit_wrapper(*args, **kwargs):
            if __output_args:
                args_print, kwargs_print = _get_timeit_arg_print(args, kwargs)
                logger.log(__level, f"sync call {func.__name__} {args_print} {kwargs_print}")
            else:
                logger.log(__level, f"sync call {func.__name__}")
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            total_time = end_time - start_time
            logger.log(__level, f"sync quit {func.__name__} Took {total_time:.3f} seconds")
            return result

        return _async_timeit_wrapper if is_async else _sync_timeit_wrapper

    return _decorator
