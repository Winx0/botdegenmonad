import os
import asyncio
from web3 import Web3
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
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

# Keyboards
menu_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
menu_keyboard.add("Buy", "Sell", "Withdraw", "Positions")

buy_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
buy_keyboard.add("ETH/MONAD", "BTC/MONAD", "Custom Pair", "🔄 Refresh Prices", "🔙 Kembali")

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    
    if 'wallet' not in user_data:
        try:
            address, private_key = create_wallet()
            await state.update_data(wallet={
                'address': address,
                'private_key': private_key
            })
            await message.answer(f"🆕 Wallet dibuat!\n📝 Alamat: `{address}`", 
                               parse_mode="Markdown")
        except Exception as e:
            await message.answer("❌ Gagal membuat wallet")
            return
    
    wallet_data = user_data['wallet']
    await message.answer(
        f"🔑 Wallet Anda:\n`{wallet_data['address']}`\n\n"
        "Pilih menu trading:",
        parse_mode="Markdown",
        reply_markup=menu_keyboard
    )

@dp.message_handler(text="Buy")
async def buy_menu(message: types.Message):
    await message.answer(
        "📈 Pilih Pair Trading:",
        reply_markup=buy_keyboard
    )

@dp.message_handler(text=["ETH/MONAD", "BTC/MONAD"])
async def handle_coin_selection(message: types.Message):
    pair = message.text
    await message.answer(f"💰 Masukkan jumlah {pair.split('/')[0]} yang ingin dibeli:")

@dp.message_handler(text="Custom Pair")
async def handle_custom_pair(message: types.Message):
    await message.answer("📥 Masukkan pair (Contoh: ETH/BTC):")

@dp.message_handler(text="🔄 Refresh Prices")
async def refresh_prices(message: types.Message):
    await message.answer("🔄 Harga Terbaru:\nETH/MONAD - $3,425.10\nBTC/MONAD - $68,150.20")

@dp.message_handler(text="🔙 Kembali")
async def back_to_menu(message: types.Message):
    await message.answer("Menu Utama:", reply_markup=menu_keyboard)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main())