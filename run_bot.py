import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))


async def main():
    from bots.bot import main as bot_main

    await bot_main()


if __name__ == "__main__":
    asyncio.run(main())
