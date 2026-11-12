import asyncio
import os
from dotenv import load_dotenv
load_dotenv()
from maxapi import Bot, Dispatcher

from routes.user_private import u_router
from routes.route_olts import olts_router


bot = Bot(os.getenv("MAX_TOKEN"))
dp = Dispatcher()

dp.include_routers(olts_router)
dp.include_routers(u_router)


async def main():
    await bot.delete_webhook()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())