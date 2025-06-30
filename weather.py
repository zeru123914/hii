import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Replace with your keys
TELEGRAM_TOKEN = "7896867377:AAE7wZrmUqGXoCFdv1M0gkwJfa3ENS4PDcU"
WEATHER_API_KEY = "657abcd22a435b369b6bee5e1bbdfe78"

# Store user states (to know when they're in /weather mode)
user_states = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = (
        "🌤️ Welcome to *Today Weather Bot!*\n\n"
        "Click one of the options below:\n"
        "`/weather` - Get today's weather\n"
        "`/help` - How to use the bot"
    )
    await update.message.reply_text(message, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = (
        "❓ *How to Use This Bot:*\n\n"
        "1. Send `/weather`\n"
        "2. The bot will ask you to enter your city name\n"
        "3. Then it will reply with today's weather\n\n"
        "Example:\n"
        "`/weather`\n"
        "`London`"
    )
    await update.message.reply_text(message, parse_mode="Markdown")

async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_states[user_id] = "waiting_for_city"
    await update.message.reply_text("🌍 Please enter your city name:")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    # Check if user is in "waiting for city name" state
    if user_states.get(user_id) == "waiting_for_city":
        city = text
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url).json()

        if response.get("cod") != 200:
            await update.message.reply_text("❌ City not found. Please try again.")
            return

        weather = response["weather"][0]["description"].title()
        temp = response["main"]["temp"]
        humidity = response["main"]["humidity"]
        wind = response["wind"]["speed"]

        reply = (
            f"📍 *City:* {city}\n"
            f"🌡️ *Temp:* {temp}°C\n"
            f"🌥️ *Condition:* {weather}\n"
            f"💧 *Humidity:* {humidity}%\n"
            f"🌬️ *Wind Speed:* {wind} m/s"
        )

        await update.message.reply_text(reply, parse_mode="Markdown")
        user_states[user_id] = None
    else:
        await update.message.reply_text("❗ Please use /start or /weather to begin.")

# Build the bot app
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("weather", weather))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("✅ Bot is running...")
app.run_polling()
