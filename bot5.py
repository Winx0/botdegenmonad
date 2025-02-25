import os
import asyncio
from web3 import Web3
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext, filters
from aiogram.dispatcher.filters.state import State, StatesGroup
from dotenv import load_dotenv

load_dotenv()

# Init Web3
RPC_URL = os.getenv("RPC_URL", "https://testnet-rpc.monad.xyz")
web3 = Web3(Web3.HTTPProvider(RPC_URL))

# Init Bot
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# State Machine
class TradeStates(StatesGroup):
    WAITING_CA = State()
    WAITING_AMOUNT = State()
    CONFIRM_BUY = State()

# Inline Keyboards
def welcome_keyboard():
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton("🚀 Generate Wallet", callback_data="generate_wallet")
    )

def main_menu():
    return InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton("💰 Buy", callback_data="menu_buy"),
        InlineKeyboardButton("📤 Sell", callback_data="menu_sell"),
        InlineKeyboardButton("🏧 Withdraw", callback_data="menu_withdraw"),
        InlineKeyboardButton("📊 Position", callback_data="menu_position"),
        InlineKeyboardButton("🔑 Export Key", callback_data="menu_export")
    )

def confirm_buy_keyboard():
    return InlineKeyboardMarkup().row(
        InlineKeyboardButton("✅ Confirm Buy", callback_data="confirm_buy"),
        InlineKeyboardButton("❌ Cancel", callback_data="cancel_buy")
    )

# ABI untuk kontrak ERC-20
ERC20_ABI = [
    {
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [{"name": "", "type": "string"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function"
    }
]

# /start command: Mengirimkan foto logo beserta caption
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    photo_url = "https://pbs.twimg.com/profile_images/1892295218910941185/pkZ39Bsy_400x400.jpg"
    await bot.send_photo(
        chat_id=message.chat.id,
        photo=photo_url,
        caption=(
            "=== BOT UJI COBA KOMUNITAS MONAD ===\n"
            "GUNAKAN DENGAN BIJAK\n"
            "LETSGO DEGEN PLAY ==="
        ),
        parse_mode="Markdown",
        reply_markup=welcome_keyboard()
    )

# Handler untuk generate wallet
@dp.callback_query_handler(lambda c: c.data == 'generate_wallet')
async def generate_wallet(callback: types.CallbackQuery, state: FSMContext):
    try:
        account = web3.eth.account.create()
        await state.update_data(wallet={
            'address': account.address,
            'private_key': account.key.hex()
        })
        # Karena pesan awal merupakan foto, kita harus mengubah caption-nya
        await callback.message.edit_caption(
            caption=(
                f"🆕 Wallet Created!\n\n"
                f"📝 Address: `{account.address}`\n\n"
                "⚠️ Simpan private key!"
            ),
            parse_mode="Markdown"
        )
        await callback.message.edit_reply_markup(reply_markup=main_menu())
    except Exception as e:
        print(f"Error creating wallet: {e}")
        await callback.message.answer("❌ Gagal membuat wallet!")

@dp.callback_query_handler(lambda c: c.data == 'menu_buy')
async def process_buy(callback: types.CallbackQuery):
    await TradeStates.WAITING_CA.set()
    await callback.message.answer(
        "📥 Masukkan Contract Address token:",
        reply_markup=ReplyKeyboardRemove()
    )

@dp.message_handler(state=TradeStates.WAITING_CA)
async def process_ca(message: types.Message, state: FSMContext):
    try:
        # Ekstrak alamat dari input
        raw_input = message.text.strip()
        ca = raw_input.split("/token/")[-1].split("/")[0] if "monadexplorer.com" in raw_input else raw_input
        ca = Web3.to_checksum_address(ca)
        
        # Validasi kontrak
        if web3.eth.get_code(ca) == b'\x00':
            return await message.reply("❌ Kontrak tidak valid!")
            
        # Dapatkan info token
        contract = web3.eth.contract(address=ca, abi=ERC20_ABI)
        symbol = contract.functions.symbol().call()
        decimals = contract.functions.decimals().call()
        
        await state.update_data(token={
            'address': ca,
            'symbol': symbol,
            'decimals': decimals
        })
        
        await TradeStates.next()
        await message.answer(
            f"✅ {symbol} Terdeteksi!\n"
            f"🔢 Decimals: {decimals}\n\n"
            "💰 Masukkan jumlah MOD yang ingin digunakan:",
            reply_markup=ReplyKeyboardRemove()
        )
        
    except Exception as e:
        print(f"Error processing contract: {e}")
        await message.reply("❌ Gagal memproses kontrak!")

@dp.message_handler(state=TradeStates.WAITING_AMOUNT)
async def process_amount(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text)
        if amount <= 0:
            raise ValueError
            
        data = await state.get_data()
        token = data['token']
        
        # Simulasi harga (1 MOD = 100 token)
        token_amount = amount * 100  # Ganti dengan price feed sebenarnya
        
        await state.update_data(amount=amount, token_amount=token_amount)
        
        await TradeStates.next()
        await message.answer(
            f"🛒 Order Beli:\n\n"
            f"• Token: {token['symbol']}\n"
            f"• Jumlah MOD: {amount}\n"
            f"• Mendapatkan: {token_amount} {token['symbol']}\n\n"
            "Konfirmasi pembelian:",
            reply_markup=confirm_buy_keyboard()
        )
        
    except ValueError:
        await message.reply("❌ Masukkan jumlah yang valid!")

@dp.callback_query_handler(lambda c: c.data == 'confirm_buy', state=TradeStates.CONFIRM_BUY)
async def confirm_buy(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    
    # Simulasi execute buy
    await callback.message.edit_text(
        f"✅ Pembelian Berhasil!\n\n"
        f"• Token: {data['token']['symbol']}\n"
        f"• Jumlah MOD: {data['amount']}\n"
        f"• Diterima: {data['token_amount']} {data['token']['symbol']}\n"
        f"• Kontrak: `{data['token']['address']}`",
        parse_mode="Markdown"
    )
    await state.finish()

@dp.callback_query_handler(lambda c: c.data == 'cancel_buy', state="*")
async def cancel_buy(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await callback.message.edit_text("❌ Pembelian dibatalkan")
    await callback.message.edit_reply_markup(None)

@dp.callback_query_handler(lambda c: c.data == 'menu_export')
async def export_key(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if 'wallet' in data:
        await callback.message.answer(
            f"🔐 Private Key:\n`{data['wallet']['private_key']}`\n\n"
            "⚠️ Jangan dibagikan!",
            parse_mode="Markdown"
        )
    else:
        await callback.message.answer("❌ Wallet belum dibuat!")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling()

if __name__ == "__main__":
    print("🔥 Bot Monad DEX aktif!")
    asyncio.run(main())
