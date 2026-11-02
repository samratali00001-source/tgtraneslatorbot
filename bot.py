import asyncio
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from deep_translator import GoogleTranslator

# আপনার বটের টোকেন এবং যে চ্যানেলে জয়েন করা বাধ্যতামূলক তার ইউজারনেম এখানে দিন
BOT_TOKEN = "9205277611:AAG5f4yvLGqyZk_6JLTmreU0yPgrrZX7emw"
REQUIRED_CHANNEL = "@DarkBugBountyHunter"  # যেমন: @DarkBugBountyHunter

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ইউজার চ্যানেলে জয়েন করেছে কিনা তা চেক করার ফাংশন
async def check_user_subscription(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=REQUIRED_CHANNEL, user_id=user_id)
        # যদি ইউজার মেম্বার, অ্যাডমিন বা ক্রিয়েটর হয়
        if member.status in ["member", "administrator", "creator"]:
            return True
        return False
    except Exception as e:
        print(f"Error checking subscription: {e}")
        return False

# /start কমান্ড হ্যান্ডলার
@dp.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    is_subscribed = await check_user_subscription(user_id)
    
    if not is_subscribed:
        # যদি সাবস্ক্রাইব করা না থাকে, তবে জয়েন করার বাটন দেখাবে
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📢 Join Channel", url=f"https://t.me/{REQUIRED_CHANNEL.replace('@', '')}")],
            [InlineKeyboardButton(text="🔄 Check Subscription", callback_data="check_sub")]
        ])
        await message.answer(
            "⚠️ **বটটি ব্যবহার করতে হলে প্রথমে আমাদের অফিসিয়াল চ্যানেলে জয়েন করতে হবে!**\n\n"
            f"দয়া করে নিচের লিংকে ক্লিক করে চ্যানেলে জয়েন করুন এবং তারপর 'Check Subscription' বাটনে ক্লিক করুন।",
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
    else:
        await message.answer(
            "👋 স্বাগতম! আপনি আমাদের চ্যানেলের সদস্য।\n\n"
            "এখন আপনি যেকোনো টেক্সট পাঠিয়ে সেটি অন্য ভাষায় অনুবাদ করতে পারেন।\n"
            "যেমন: ইংরেজি থেকে বাংলা বা অন্য কোনো ভাষা।"
        )

# সাবস্ক্রাইব চেক করার বাটন কলব্যাক
@dp.callback_query(F.data == "check_sub")
async def verify_subscription(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    is_subscribed = await check_user_subscription(user_id)
    
    if is_subscribed:
        await callback.message.edit_text(
            "✅ ধন্যবাদ! আপনার সাবস্ক্রিপশন নিশ্চিত করা হয়েছে। এখন থেকে আপনি বট ব্যবহার করতে পারবেন।"
        )
    else:
        await callback.answer("❌ আপনি এখনো চ্যানেলে জয়েন করেননি! দয়া করে আগে জয়েন করুন।", show_alert=True)

# সাধারণ টেক্সট অনুবাদ করার হ্যান্ডলার
@dp.message(F.text & ~F.text.startswith("/"))
async def translate_text(message: Message):
    user_id = message.from_user.id
    
    # মেসেজ প্রসেস করার আগেও সাবস্ক্রিপশন চেক করতে পারেন
    if not await check_user_subscription(user_id):
        await message.answer("⚠️ বট ব্যবহার করতে আগে আমাদের চ্যানেলে জয়েন করুন। /start লিখে আবার চেষ্টা করুন।")
        return

    text = message.text
    try:
        # ডিফল্টভাবে ইংরেজি থেকে বাংলা অনুবাদ (আপনি চাইলে এটি পরিবর্তন করতে পারেন)
        translated = GoogleTranslator(source='auto', target='bn').translate(text)
        await message.answer(f"🌐 **অনুবাদ (Translation):**\n\n{translated}", parse_mode="Markdown")
    except Exception as e:
        await message.answer("দুঃখিত, অনুবাদ করতে সমস্যা হয়েছে। আবার চেষ্টা করুন।")

# মেইন ফাংশন
async def main():
    print("Bot is starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
