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

# Inline Keyboards
def welcome_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("🚀 Generate Wallet", callback_data="generate_wallet"))
    return keyboard

def main_menu():
    menu = InlineKeyboardMarkup(row_width=2)
    menu.add(
        InlineKeyboardButton("💰 Buy", callback_data="menu_buy"),
        InlineKeyboardButton("📤 Sell", callback_data="menu_sell"),
        InlineKeyboardButton("🏧 Withdraw", callback_data="menu_withdraw"),
        InlineKeyboardButton("📊 Position", callback_data="menu_position"),
        InlineKeyboardButton("🔑 Export Private Key", callback_data="menu_export")
    )
    return menu

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    welcome_text = (
        "=== INI ADALAH BOT UJI COBA UNTUK KOMUNITAS MONAD ===\n"
        "HARAP GUNAKAN DENGAN BIJAK\n"
        "LETSGO DEGEN PLAY ==="
    )
    await message.answer(welcome_text, reply_markup=welcome_keyboard())

@dp.callback_query_handler(lambda c: c.data == 'generate_wallet')
async def generate_wallet(callback: types.CallbackQuery, state: FSMContext):
    try:
        account = web3.eth.account.create()
        address = account.address
        private_key = account.key.hex()
        
        await state.update_data(wallet={
            'address': address,
            'private_key': private_key
        })
        
        response = (
            f"🆕 Wallet Created!\n\n"
            f"📝 Address: `{address}`\n\n"
            "⚠️ Simpan private key dengan aman!"
        )
        await callback.message.edit_text(response, parse_mode="Markdown")
        await callback.message.edit_reply_markup(main_menu())
        
    except Exception as e:
        await callback.message.answer("❌ Gagal membuat wallet!")

@dp.callback_query_handler(lambda c: c.data == 'menu_buy')
async def process_buy(callback: types.CallbackQuery):
    await callback.message.answer("📥 Silakan masukkan Contract Address token:")
    # Tambahkan logic untuk menerima CA token selanjutnya

@dp.callback_query_handler(lambda c: c.data == 'menu_export')
async def export_private_key(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    wallet = data.get('wallet', {})
    
    if wallet:
        await callback.message.answer(
            f"🔐 Private Key Anda:\n`{wallet['private_key']}`\n\n"
            "⚠️ Jangan berikan ini ke siapa pun!",
            parse_mode="Markdown"
        )
    else:
        await callback.message.answer("❌ Wallet belum dibuat!")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main())