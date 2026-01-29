import os
import time
from fastapi import Request

def now_ms(request: Request) -> int:
    if os.getenv("TEST_MODE") == "1":
        header_time = request.headers.get("x-test-now-ms")
        if header_time:
            try:
                return int(header_time)
            except ValueError:
                pass
    return int(time.time() * 1000)
