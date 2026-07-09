"""
装饰器工具集
"""
import time
import functools
from utils.logger import get_logger

logger = get_logger("decorators")

def retry(max_times: int = 3, delay: float = 1.0):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_times):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(f"第{attempt + 1}次调用失败: {e}")
                    if attempt < max_times - 1:
                        time.sleep(delay)
            raise last_exception
        return wrapper
    return decorator

def log_execution(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"开始执行: {func.__name__}")
        start = time.time()
        try:
            result = func(*args, **kwargs)
            cost = time.time() - start
            logger.info(f"执行完成: {func.__name__}, 耗时{cost:.2f}s")
            return result
        except Exception as e:
            logger.error(f"执行失败: {func.__name__}, 错误: {e}")
            raise
    return wrapper
