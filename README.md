# Bot Degen Monad

Bot Degen Monad adalah sebuah bot Telegram untuk uji coba fitur trading di jaringan Monad. Bot ini dibangun menggunakan Python dengan library [aiogram](https://docs.aiogram.dev/) untuk integrasi Telegram dan [web3.py](https://github.com/ethereum/web3.py) untuk berinteraksi dengan blockchain.

## Fitur Utama

- **Generate Wallet:** Membuat wallet baru dengan alamat dan private key.
- **Token Trading:** Fitur pembelian token menggunakan MOD.
- **Konfirmasi Transaksi:** Konfirmasi pembelian melalui inline keyboard.
- **Export Key:** Menampilkan private key yang dihasilkan (jangan bagikan kepada siapapun!).

## Persyaratan

- Python 3.8 ke atas
- [aiogram](https://docs.aiogram.dev/)
- [web3.py](https://github.com/ethereum/web3.py)
- [python-dotenv](https://github.com/theskumar/python-dotenv)

## Instalasi

1. **Clone repository ini:**

   ```bash
   git clone https://github.com/Winx0/botdegenmonad.git
   cd botdegenmonad
