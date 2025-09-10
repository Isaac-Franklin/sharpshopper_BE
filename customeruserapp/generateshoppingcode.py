
import datetime


def generate_unique_code(prefix="CODE"):
    # Get current time down to microseconds
    now = datetime.datetime.now()
    time_str = now.strftime('%Y%m%d%H%M%S%f')  # e.g. '20250807115723987654'
    print(f"{prefix}-{time_str}")
    return f"{prefix}-{time_str}"


