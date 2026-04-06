import asyncio
import os

#Debug tools - you can add it to any test. How to run test with debug pause: DEBUG_UI_WAIT=1 pytest tests/user_service/test_delete_user.py
def is_debug_ui_wait_enabled() -> bool:
    return os.getenv("DEBUG_UI_WAIT") == "1"


async def debug_pause(message: str, seconds: int = 20) -> None:
    if is_debug_ui_wait_enabled():
        print(message)
        await asyncio.sleep(seconds)
