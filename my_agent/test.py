import time
import functools
import logging
import random
from typing import Callable, Tuple, Type, Union

# Configure a default logger for the module if no custom logger is provided
# In a real application, you'd typically configure logging globally.
logger = logging.getLogger(__name__)
if not logger.handlers: # Avoid adding handlers multiple times if module is reloaded
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def retry(
    tries: int = 3,
    delay: Union[int, float] = 1,
    backoff: Union[int, float] = 2,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    logger: logging.Logger = logger, # Allow custom logger
    jitter: Union[int, float] = 0, # Max percentage/absolute value of jitter to add to delay
) -> Callable:
    """
    Decorator to retry a function if it raises specific exceptions.

    Args:
        tries (int): Number of attempts to make (including the first one).
        delay (Union[int, float]): Initial delay in seconds between retries.
        backoff (Union[int, float]): Multiplier by which the delay increases after each failed attempt.
        exceptions (Tuple[Type[Exception], ...]): A tuple of exception types to catch and retry on.
                                            If any other exception is raised, it will not be retried.
        logger (logging.Logger): The logger instance to use for retry messages.
        jitter (Union[int, float]): Maximum random jitter to add to the delay.
                                    If jitter > 0 and jitter < 1, it's a percentage (e.g., 0.1 for 10%).
                                    If jitter >= 1, it's an absolute value in seconds.
    """
    if tries < 1:
        raise ValueError("tries must be at least 1")
    if delay < 0:
        raise ValueError("delay must be non-negative")
    if backoff < 1:
        raise ValueError("backoff must be at least 1")
    if not isinstance(exceptions, tuple):
        raise TypeError("exceptions must be a tuple of Exception types")

    def deco_retry(f: Callable) -> Callable:
        @functools.wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except exceptions as e:
                    # Calculate actual sleep delay with jitter
                    current_delay = mdelay
                    if jitter > 0:
                        if jitter < 1: # Interpret as percentage
                            jitter_amount = random.uniform(0, current_delay * jitter)
                        else: # Interpret as absolute value
                            jitter_amount = random.uniform(0, jitter)
                        current_delay += jitter_amount

                    logger.warning(
                        f"Retrying {f.__name__!r} in {current_delay:.2f} seconds... "
                        f"({mtries - 1} tries left) due to: {type(e).__name__}: {e}"
                    )
                    time.sleep(current_delay)
                    mtries -= 1
                    mdelay *= backoff
            
            # Last attempt outside the loop to re-raise if it fails
            return f(*args, **kwargs)

        return f_retry
    return deco_retry


if __name__ == '__main__':
    # Ensure the default logger shows INFO messages in the example output
    # if it hasn't been configured by the application already.
    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    # Example 1: Basic retry on any exception with logging and jitter
    @retry(tries=4, delay=1, backoff=2, jitter=0.5) # 0.5 seconds max jitter
    def flaky_function_any_exception(attempt_num_ref):
        attempt_num_ref[0] += 1
        logger.info(f"  Attempt {attempt_num_ref[0]} for flaky_function_any_exception...")
        if attempt_num_ref[0] < 3: # Succeeds on the 3rd attempt
            raise ValueError("Simulated network error or transient issue!")
        logger.info("  flaky_function_any_exception succeeded!")
        return "Success!"

    logger.info("--- Testing flaky_function_any_exception ---")
    try:
        attempt_counter = [0]
        result = flaky_function_any_exception(attempt_counter)
        logger.info(f"Result: {result}\n")
    except Exception as e:
        logger.error(f"flaky_function_any_exception failed permanently: {e}\n")


    # Example 2: Retry on specific exception types only with custom logger and percentage jitter
    custom_logger = logging.getLogger("network_logger")
    custom_logger.setLevel(logging.DEBUG)
    if not custom_logger.handlers:
        custom_logger.addHandler(logging.StreamHandler())
        # Add a formatter to the custom logger handler too
        custom_logger.handlers[0].setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))


    @retry(tries=3, delay=0.5, backoff=3, exceptions=(ConnectionError, TimeoutError), logger=custom_logger, jitter=0.2) # 20% delay jitter
    def network_operation():
        rand = random.random()
        custom_logger.debug(f"  Performing network operation... (random: {rand:.2f})")
        if rand < 0.4:
            raise ConnectionError("Connection lost!")
        elif rand < 0.7:
            raise TimeoutError("Request timed out!")
        elif rand < 0.8:
            raise PermissionError("Access denied!") # This will NOT be retried
        custom_logger.info("  Network operation succeeded!")
        return "Data received!"

    logger.info("--- Testing network_operation ---")
    for i in range(2):
        logger.info(f"Run {i+1}:")
        try:
            result = network_operation()
            logger.info(f"Result: {result}\n")
        except Exception as e:
            logger.error(f"network_operation failed permanently: {e} (Type: {type(e).__name__})\n")


    # Example 3: Function that always fails
    @retry(tries=3, delay=0.1)
    def always_fails():
        logger.info("  Attempting always_fails...")
        raise RuntimeError("This function always fails!")

    logger.info("--- Testing always_fails ---")
    try:
        always_fails()
    except RuntimeError as e:
        logger.error(f"always_fails finally failed as expected: {e}\n")