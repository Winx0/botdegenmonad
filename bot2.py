import os
import asyncio
from web3 import Web3
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from dotenv import load_dotenv

load_dotenv()

# Init Web3
RPC_URL = os.getenv("RPC_URL", "https://testnet-rpc.monad.xyz")
web3 = Web3(Web3.HTTPProvider(RPC_URL))

# Init Bot
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

def create_wallet():
    account = web3.eth.account.create()
    return account.address, account.key.hex()

# Inline Keyboards
def main_menu():
    menu = InlineKeyboardMarkup(row_width=2)
    menu.add(
        InlineKeyboardButton("💰 Buy", callback_data="menu_buy"),
        InlineKeyboardButton("📤 Sell", callback_data="menu_sell"),
        InlineKeyboardButton("🏧 Withdraw", callback_data="menu_withdraw"),
        InlineKeyboardButton("📊 Positions", callback_data="menu_positions")
    )
    return menu

def buy_menu():
    menu = InlineKeyboardMarkup(row_width=2)
    menu.add(
        InlineKeyboardButton("ETH/MONAD", callback_data="buy_eth"),
        InlineKeyboardButton("BTC/MONAD", callback_data="buy_btc"),
        InlineKeyboardButton("Custom Pair", callback_data="buy_custom"),
        InlineKeyboardButton("🔄 Refresh", callback_data="buy_refresh"),
        InlineKeyboardButton("🔙 Back", callback_data="menu_main")
    )
    return menu

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    address, private_key = create_wallet()
    await message.answer(
        f"🆕 Wallet Created!\n\n"
        f"📝 Address: `{address}`\n\n"
        "Select action:",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )

@dp.callback_query_handler(lambda c: c.data == 'menu_main')
async def process_main_menu(callback: types.CallbackQuery):
    await callback.message.edit_reply_markup(reply_markup=main_menu())

@dp.callback_query_handler(lambda c: c.data == 'menu_buy')
async def process_buy_menu(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "📈 Select Trading Pair:",
        reply_markup=buy_menu()
    )

@dp.callback_query_handler(lambda c: c.data.startswith('buy_'))
async def process_buy_selection(callback: types.CallbackQuery):
    action = callback.data.split('_')[1]
    
    if action == 'eth':
        await callback.message.answer("💰 Enter ETH amount:")
    elif action == 'btc':
        await callback.message.answer("💰 Enter BTC amount:")
    elif action == 'custom':
        await callback.message.answer("📥 Enter custom pair (e.g. ETH/BTC):")
    elif action == 'refresh':
        await callback.message.answer("🔄 Prices Refreshed!\nETH/MONAD: $3,425.10\nBTC/MONAD: $68,150.20")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main())