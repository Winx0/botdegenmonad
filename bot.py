import os
import asyncio
from web3 import Web3
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv

# Load variabel dari file .env
load_dotenv()

# Konfigurasi RPC Monad Testnet
RPC_URL = os.getenv("RPC_URL", "https://testnet-rpc.monad.xyz")
web3 = Web3(Web3.HTTPProvider(RPC_URL))

# Setup bot Telegram dengan error handling
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Nama variabel yang benar

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("Token bot Telegram tidak ditemukan. Pastikan sudah diatur di .env")

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# Fungsi untuk membuat wallet baru dengan error handling
def create_wallet():
    try:
        account = web3.eth.account.create()
        return account.address, account.key.hex()
    except Exception as e:
        raise RuntimeError(f"Gagal membuat wallet: {str(e)}")

# Tombol menu utama
menu_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
menu_keyboard.add(
    KeyboardButton("Buy"),
    KeyboardButton("Sell"),
    KeyboardButton("Withdraw"),
    KeyboardButton("Positions")
)

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    try:
        address, private_key = create_wallet()
        # Hapus penyimpanan private key langsung (tidak aman)
        await message.answer(
            f"🆕 Wallet sementara telah dibuat!\n\n"
            f"📝 Alamat: `{address}`\n\n"
            "⚠️ *Jangan simpan aset di wallet ini!*",
            parse_mode="Markdown"
        )
        await message.answer("✅ Pilih menu di bawah:", reply_markup=menu_keyboard)
    except Exception as e:
        await message.answer("❌ Gagal membuat wallet. Silakan coba lagi.")

# Handler untuk state
@dp.message_handler(lambda message: message.text == "Buy")
async def buy_token(message: types.Message):
    await message.answer("📥 Masukkan Contract Address token yang ingin dibeli:")

@dp.message_handler(lambda message: message.text == "Withdraw")
async def withdraw_funds(message: types.Message):
    await message.answer("🔗 Masukkan alamat tujuan untuk Withdraw:")

# Error handler umum
@dp.errors_handler()
async def errors_handler(update, error):
    print(f"Terjadi error: {error}")
    return True

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot dihentikan")