from typing import Optional

import g4f


async def ask_ai(promt: str) -> Optional[str]:
    try:
        response = await g4f.ChatCompletion.create_async(
            model=g4f.models.gpt_4,
            messages=[{"role": "user", "content": promt}]
        )
    except Exception:
        return None
    return response
