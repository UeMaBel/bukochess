import time as time_module


def measure_time(func):
    def wrapper(*args, **kwargs):
        start_time = time_module.time()  # Start timer
        result = func(*args, **kwargs)  # Call the original function
        end_time = time_module.time()  # End timer
        elapsed_time = end_time - start_time
        # if elapsed_time > 0.05:
        print(f"{func.__name__} executed in {elapsed_time:.2f} seconds")
        return result  # Return the result of the original function

    return wrapper
