import logging
import pandas as pd
import os
from flask import Flask
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# ✅ Initialize Flask app (for Railway deployment)
app = Flask(__name__)

# ✅ Telegram Bot Token (Use environment variable)
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ✅ Start command
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hello! Send me a CSV or Excel file, and I'll process it.")

# ✅ Handle document (CSV/Excel)
def handle_document(update: Update, context: CallbackContext):
    file = update.message.document
    file_name = file.file_name
    file_path = f"./{file_name}"

    # ✅ Download file
    new_file = context.bot.get_file(file.file_id)
    new_file.download(file_path)
    update.message.reply_text(f"File received: {file_name}\nProcessing...")

    try:
        # ✅ Load CSV or Excel
        if file_name.endswith(".csv"):
            df = pd.read_csv(file_path, encoding="latin1")
        elif file_name.endswith(".xls") or file_name.endswith(".xlsx"):
            df = pd.read_excel(file_path)
        else:
            update.message.reply_text("Unsupported file format. Please send a CSV or Excel file.")
            return
        
        # ✅ Filter rows where AGEING > 7
        df_filtered = df[df["AGEING"] > 7][["CALL ID", "CUSTOMER NAME", "CALL STAGE", "PENDING PARTS", "AGEING"]]

        # ✅ Convert dataframe to text format
        result_text = df_filtered.to_string(index=False)

        # ✅ Send response (split if too long)
        if len(result_text) > 4000:
            result_text = "Too many records to send at once. Please filter further."
        
        update.message.reply_text(f"Filtered Results:\n{result_text}")

    except Exception as e:
        update.message.reply_text(f"❌ Error processing the file: {e}")

    # ✅ Cleanup
    os.remove(file_path)

# ✅ Error handler
def error_handler(update: Update, context: CallbackContext):
    logging.error(f"Exception while handling an update: {context.error}")

# ✅ Run Flask Server for Railway
@app.route('/')
def home():
    return "Telegram Bot is Running!"

# ✅ Main function
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    # ✅ Add handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.document, handle_document))
    dp.add_error_handler(error_handler)

    # ✅ Start bot polling
    updater.start_polling()

    # ✅ Run Flask on Railway-assigned port
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

# ✅ Run bot
if __name__ == "__main__":
    main()
