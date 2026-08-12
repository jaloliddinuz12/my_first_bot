import asyncio
import random
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from aiogram.enums import ParseMode

# ==================== SOZLAMALAR ====================
BOT_TOKEN = "8644628669:AAFv_1XdVwCEN0x4Cuf5eBn3dvdh99MYqeY"  # @BotFather dan olingan token

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ==================== O'YIN QOIDALARI ====================
WIN_RULES = {
    "🤛": "✌️",  # Tosh qaychini yutadi
    "✌️": "✋",   # Qaychi qog'ozni yutadi
    "✋": "🤛"    # Qog'oz toshni yutadi
}

EMOJIS = ["🤛", "✌️", "✋"]
NAMES = {
    "🤛": "Tosh 🪨",
    "✌️": "Qaychi ✂️",
    "✋": "Qog'oz 📄"
}

# ==================== O'YIN HOLATI ====================
game_sessions = {}

class GameSession:
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.players = {}  # {user_id: {"username": str, "choice": str}}
        self.game_active = False
        self.message_id = None
        self.waiting_for_players = False

    def add_player(self, user_id, username, choice=None):
        """O'yinchini qo'shish. Endi bu funksiya faqat variant tanlangan
        paytda chaqiriladi, ya'ni 'ishtirokchi bo'lish' = 'variant tanlash'."""
        if user_id not in self.players and len(self.players) < 2:
            self.players[user_id] = {"username": username, "choice": choice}
            return True
        return False

    def set_choice(self, user_id, choice):
        """Tanlovni saqlash"""
        if user_id in self.players:
            self.players[user_id]["choice"] = choice
            return True
        return False

    def all_players_chose(self):
        """Ikkala o'yinchi ham tanladimi?"""
        return len(self.players) == 2 and all(p["choice"] is not None for p in self.players.values())

    def get_winner(self):
        """G'olibni aniqlash"""
        players_list = list(self.players.items())
        player1_id, player1_data = players_list[0]
        player2_id, player2_data = players_list[1]

        if player1_data["choice"] == player2_data["choice"]:
            return "draw"
        elif WIN_RULES.get(player1_data["choice"]) == player2_data["choice"]:
            return player1_id
        else:
            return player2_id

    def reset(self):
        """O'yinni tozalash"""
        self.players = {}
        self.game_active = False
        self.message_id = None
        self.waiting_for_players = False

# ==================== KLAVIATURALAR ====================
def get_mode_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🤖 Bot bilan o'ynash", callback_data="mode_solo"),
                InlineKeyboardButton(text="👥 Ikki kishilik", callback_data="mode_duel")
            ],
            [
                InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_game")
            ]
        ]
    )
    return keyboard

def get_game_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🤛 Tosh", callback_data="choice_🤛"),
                InlineKeyboardButton(text="✌️ Qaychi", callback_data="choice_✌️"),
                InlineKeyboardButton(text="✋ Qog'oz", callback_data="choice_✋")
            ],
            [
                InlineKeyboardButton(text="❌ O'yinni to'xtatish", callback_data="cancel_game")
            ]
        ]
    )
    return keyboard

def get_start_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎮 Yangi o'yin boshlash", callback_data="start_game")]
        ]
    )
    return keyboard

def get_solo_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🤛 Tosh", callback_data="solo_choice_🤛"),
                InlineKeyboardButton(text="✌️ Qaychi", callback_data="solo_choice_✌️"),
                InlineKeyboardButton(text="✋ Qog'oz", callback_data="solo_choice_✋")
            ],
            [
                InlineKeyboardButton(text="❌ O'yinni to'xtatish", callback_data="cancel_solo_game")
            ]
        ]
    )
    return keyboard

# ==================== BOT BUYRUKLARI ====================
@dp.message(Command("start"))
async def start_command(message: Message):
    welcome_text = (
        "🎮 TOSH - QAYCHI - QOG'OZ 🎮\n\n"
        "👋 Xush kelibsiz!\n\n"
        "📌 O'yin rejimlari:\n"
        "🤖 Bot bilan - Kompyuterga qarshi o'ynang (shaxsiy chatda)\n"
        "👥 Ikki kishilik - Guruhda boshqa o'yinchi bilan\n\n"
        "📊 Qoidalar:\n"
        "• 🤛 Tosh ✌️ Qaychini yutadi\n"
        "• ✌️ Qaychi ✋ Qog'ozni yutadi\n"
        "• ✋ Qog'oz 🤛 Toshlarni yutadi\n"
        "• Bir xil variantda durrang\n\n"
        "🎯 Buyruqlar:\n"
        "/game - O'yinni boshlash\n"
        "/help - Yordam\n"
        "/cancel - O'yinni bekor qilish"
    )

    await message.answer(
        welcome_text,
        parse_mode=None,
        reply_markup=get_start_keyboard()
    )

@dp.message(Command("help"))
async def help_command(message: Message):
    help_text = (
        "❓ Yordam ❓\n\n"
        "🎮 O'yin buyruqlari:\n"
        "/game - Yangi o'yin boshlash\n"
        "/cancel - Joriy o'yinni bekor qilish\n"
        "/start - Botni qayta ishga tushirish\n"
        "/help - Bu xabarni ko'rsatish\n\n"
        "👥 Guruhda o'ynash:\n"
        "1. Botni guruhga qo'shing\n"
        "2. Botni admin qiling\n"
        "3. /game yozing va Ikki kishilik rejimni tanlang\n"
        "4. Guruhdagi istalgan 2 nafar a'zo variant tugmalaridan birini bossa,\n"
        "   ular avtomatik ravishda o'yinchi bo'ladi\n"
        "5. 2 kishi variant tanlagach, natija chiqariladi\n\n"
        "📊 O'yin qoidalari:\n"
        "• 🤛 Tosh ✌️ Qaychini yutadi\n"
        "• ✌️ Qaychi ✋ Qog'ozni yutadi\n"
        "• ✋ Qog'oz 🤛 Toshlarni yutadi\n"
        "• Bir xil variantda durrang"
    )

    await message.answer(help_text, parse_mode=None)

@dp.message(Command("game"))
async def game_command(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.full_name

    # Agar shaxsiy chat bo'lsa - bot bilan o'ynash
    if message.chat.type == "private":
        game_text = (
            f"🎮 TOSH - QAYCHI - QOG'OZ 🎮\n\n"
            f"🤖 Bot bilan o'ynash rejimi\n"
            f"👤 O'yinchi: {username}\n\n"
            f"📌 Variant tanlang:"
        )

        await message.answer(
            game_text,
            parse_mode=None,
            reply_markup=get_solo_keyboard()
        )
        return

    # Guruhda o'ynash
    if chat_id not in game_sessions:
        game_sessions[chat_id] = GameSession(chat_id)

    session = game_sessions[chat_id]

    # Agar o'yin faol bo'lsa - hozirgi holatni ko'rsatamiz
    # (bu yerda hech kim avtomatik o'yinchi qilib qo'shilmaydi,
    # faqat variant tanlangandagina ishtirokchi bo'ladi)
    if session.game_active:
        if len(session.players) >= 2:
            await message.answer("⚠️ O'yinda allaqachon 2 kishi qatnashyapti. Keyingi o'yinda qatnashing!")
            return

        game_text = f"🎮 TOSH - QAYCHI - QOG'OZ 🎮\n\n"
        game_text += f"👥 Ikki kishilik rejim\n\n"

        if session.players:
            for i, player in enumerate(session.players.values(), 1):
                # Diqqat: tanlangan variant atayin ko'rsatilmaydi, aks holda
                # keyingi o'yinchi shunchaki yutadigan variantni tanlab qo'yadi
                game_text += f"{i}. {player['username']} - ✅ Tanladi (variant yashirin)\n"
            game_text += f"\n⏳ Yana bir o'yinchi kerak!\n"
            game_text += f"📌 Guruh a'zolaridan istalgan biri variant tanlasin:"
        else:
            game_text += f"⏳ Hali hech kim ishtirok etmayapti.\n"
            game_text += f"📌 Guruh a'zolaridan istalgan 2 kishi pastdagi variantlardan birini tanlasin!"

        await message.answer(
            game_text,
            parse_mode=None,
            reply_markup=get_game_keyboard()
        )
        return

    # Yangi o'yin boshlash - rejim tanlash
    session.reset()
    session.game_active = True

    mode_text = (
        "🎮 O'yin rejimini tanlang:\n\n"
        "🤖 Bot bilan o'ynash - Sizni shaxsiy chatga olib boradi\n"
        "👥 Ikki kishilik - Guruhda boshqa o'yinchi bilan\n\n"
        "Tanlovingizni pastdagi tugmalar orqali qiling:"
    )

    await message.answer(
        mode_text,
        parse_mode=None,
        reply_markup=get_mode_keyboard()
    )

@dp.message(Command("cancel"))
async def cancel_command(message: Message):
    chat_id = message.chat.id

    if chat_id in game_sessions:
        session = game_sessions[chat_id]
        session.reset()
        await message.answer("❌ O'yin bekor qilindi!", reply_markup=get_start_keyboard())
    else:
        await message.answer("⚠️ Hozirda faol o'yin mavjud emas.")

# ==================== INLINE TUGMALAR ====================
@dp.callback_query(lambda c: c.data == "start_game")
async def start_game_callback(callback: CallbackQuery):
    await callback.answer()
    try:
        message = callback.message
        await game_command(message)
    except Exception as e:
        print(f"Xatolik: {e}")

@dp.callback_query(lambda c: c.data == "cancel_game")
async def cancel_game_callback(callback: CallbackQuery):
    try:
        await callback.answer()
        chat_id = callback.message.chat.id

        if chat_id in game_sessions:
            session = game_sessions[chat_id]
            session.reset()
            await callback.message.edit_text(
                "❌ O'yin to'xtatildi!",
                reply_markup=get_start_keyboard()
            )
        else:
            await callback.message.edit_text("⚠️ Faol o'yin mavjud emas.")
    except Exception as e:
        print(f"Xatolik: {e}")

@dp.callback_query(lambda c: c.data == "cancel_solo_game")
async def cancel_solo_game_callback(callback: CallbackQuery):
    try:
        await callback.answer()
        await callback.message.edit_text(
            "❌ O'yin to'xtatildi!",
            reply_markup=get_start_keyboard()
        )
    except Exception as e:
        print(f"Xatolik: {e}")

@dp.callback_query(lambda c: c.data and c.data.startswith("mode_"))
async def mode_callback(callback: CallbackQuery):
    try:
        await callback.answer()

        mode = callback.data.split("_")[1]
        chat_id = callback.message.chat.id
        username = callback.from_user.username or callback.from_user.full_name

        if mode == "solo":
            # Bot bilan o'ynash - shaxsiy chatga yo'naltirish
            bot_info = await bot.get_me()
            bot_username = bot_info.username

            await callback.message.edit_text(
                f"🤖 Bot bilan o'ynash rejimi tanlandi!\n\n"
                f"👤 {username}, men bilan shaxsiy chatda o'ynash uchun pastdagi tugmani bosing:\n\n"
                f"💡 @{bot_username} ga yozing yoki pastdagi tugmani bosing",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [InlineKeyboardButton(
                            text="🤖 Shaxsiy chatda o'ynash",
                            url=f"https://t.me/{bot_username}"
                        )],
                        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_game")]
                    ]
                )
            )
            return

        elif mode == "duel":
            # Ikki kishilik - guruhda davom etadi.
            # MUHIM: tugmani bosgan kishi avtomatik o'yinchi bo'lmaydi.
            # O'yinchi bo'lish uchun keyingi bosqichda variant (Tosh/Qaychi/Qog'oz)
            # tanlash kerak - buni istalgan guruh a'zosi qila oladi.
            if chat_id not in game_sessions:
                game_sessions[chat_id] = GameSession(chat_id)

            session = game_sessions[chat_id]

            session.reset()
            session.game_active = True

            game_text = (
                f"🎮 TOSH - QAYCHI - QOG'OZ 🎮\n\n"
                f"👥 Ikki kishilik rejim\n\n"
                f"⏳ Hali hech kim ishtirok etmayapti.\n"
                f"📌 Guruh a'zolaridan istalgan 2 kishi pastdagi variantlardan\n"
                f"birini tanlasa, ular o'yinchi bo'ladi!"
            )

            await callback.message.edit_text(
                game_text,
                parse_mode=None,
                reply_markup=get_game_keyboard()
            )
    except Exception as e:
        print(f"Xatolik: {e}")

@dp.callback_query(lambda c: c.data and c.data.startswith("solo_choice_"))
async def solo_choice_callback(callback: CallbackQuery):
    try:
        await callback.answer()

        choice = callback.data.split("_")[2]

        # Bot variantni random tanlaydi
        bot_choice = random.choice(EMOJIS)

        # Natijani aniqlash
        if choice == bot_choice:
            result = "draw"
        elif WIN_RULES.get(choice) == bot_choice:
            result = "win"
        else:
            result = "lose"

        result_text = f"🎮 TOSH - QAYCHI - QOG'OZ 🎮\n\n"
        result_text += f"👤 Siz: {choice} {NAMES[choice]}\n"
        result_text += f"🤖 Bot: {bot_choice} {NAMES[bot_choice]}\n\n"

        if result == "draw":
            result_text += "🤝 DURRANG! 🤝"
        elif result == "win":
            result_text += "🎉 SIZ YUTDINGIZ! 🎉"
        else:
            result_text += "😔 BOT YUTDI! 😔"

        await callback.message.edit_text(
            result_text,
            parse_mode=None,
            reply_markup=get_start_keyboard()
        )
    except Exception as e:
        print(f"Xatolik: {e}")

@dp.callback_query(lambda c: c.data and c.data.startswith("choice_"))
async def choice_callback(callback: CallbackQuery):
    try:
        await callback.answer()

        choice = callback.data.split("_")[1]
        chat_id = callback.message.chat.id
        user_id = callback.from_user.id
        username = callback.from_user.username or callback.from_user.full_name

        if chat_id not in game_sessions:
            await callback.message.edit_text(
                "⚠️ O'yin mavjud emas. /game buyrug'ini yuboring.",
                reply_markup=get_start_keyboard()
            )
            return

        session = game_sessions[chat_id]

        # Agar o'yin faol bo'lmasa
        if not session.game_active:
            await callback.message.edit_text(
                "⚠️ O'yin tugagan. Yangi o'yin boshlash uchun /game yozing.",
                reply_markup=get_start_keyboard()
            )
            return

        # Agar user allaqachon tanlov qilgan (ya'ni allaqachon o'yinchi) bo'lsa
        if user_id in session.players:
            await callback.answer("⚠️ Siz allaqachon tanlov qilgansiz!", show_alert=True)
            return

        # Agar 2 kishi allaqachon o'yinchi bo'lib bo'lgan bo'lsa
        if len(session.players) >= 2:
            await callback.answer("⚠️ O'yinda 2 kishi qatnashyapti!", show_alert=True)
            return

        # MUHIM: variant tanlash = o'yinchi bo'lish. Tugmani bosgan har qanday
        # guruh a'zosi shu yerda birinchi marta o'yinchi sifatida qo'shiladi
        # va tanlovi darhol saqlanadi.
        session.add_player(user_id, username, choice)

        # O'yin holatini ko'rsatish
        game_text = f"🎮 TOSH - QAYCHI - QOG'OZ 🎮\n\n"
        game_text += f"👥 Ikki kishilik rejim\n"

        player_list = list(session.players.items())
        for i, (uid, data) in enumerate(player_list, 1):
            name = data["username"]
            # Diqqat: variant atayin ko'rsatilmaydi - aks holda ikkinchi
            # o'yinchi birinchisining tanlovini ko'rib, uni yutadigan
            # variantni ataylab tanlab olishi mumkin bo'lardi
            game_text += f"{i}. {name} - ✅ Tanladi (variant yashirin)\n"

        # Ikkala o'yinchi ham tanlov qilganmi?
        if session.all_players_chose():
            # Natijani aniqlash
            winner = session.get_winner()

            player1_name = player_list[0][1]["username"]
            player1_choice = player_list[0][1]["choice"]
            player2_name = player_list[1][1]["username"]
            player2_choice = player_list[1][1]["choice"]

            result_text = f"🎮 TOSH - QAYCHI - QOG'OZ 🎮\n\n"
            result_text += f"1️⃣ {player1_name}: {player1_choice} {NAMES[player1_choice]}\n"
            result_text += f"2️⃣ {player2_name}: {player2_choice} {NAMES[player2_choice]}\n\n"

            if winner == "draw":
                result_text += "🤝 DURRANG! 🤝"
            else:
                winner_name = session.players[winner]["username"]
                result_text += f"🎉 {winner_name} YUTDI! 🎉"

            session.reset()

            await callback.message.edit_text(
                result_text,
                parse_mode=None,
                reply_markup=get_start_keyboard()
            )
        else:
            # Hali faqat 1 kishi tanlov qilgan
            game_text += f"\n⏳ Yana bir o'yinchi kerak!\n"
            game_text += f"📌 Guruhdagi boshqa a'zo variant tanlasin (bir xil odam ikkinchi marta tanlay olmaydi):"

            await callback.message.edit_text(
                game_text,
                parse_mode=None,
                reply_markup=get_game_keyboard()
            )
    except Exception as e:
        print(f"Xatolik: {e}")

# ==================== BOTNI ISHGA TUSHIRISH ====================
async def main():
    bot_info = await bot.get_me()
    bot.username = bot_info.username

    print(f"🤖 Bot ishga tushmoqda: @{bot.username}")
    print("✅ Bot tayyor!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())