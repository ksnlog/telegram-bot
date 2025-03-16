import os
import pandas as pd
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# ✅ Replace with your actual Telegram Bot Token
TOKEN = "7872312703:AAGghF_wMoFzbxzXWhSVvCnUeJ5kw9zXMqk"

# ✅ Enable logging
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

# ✅ Start command handler
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Hello! Send me a CSV or Excel file, and I'll process it.")

# ✅ File handler (process CSV or Excel)
async def handle_document(update: Update, context: CallbackContext) -> None:
    document = update.message.document
    file_path = f"downloads/{document.file_name}"

    # ✅ Download the file
    os.makedirs("downloads", exist_ok=True)
    file = await context.bot.get_file(document.file_id)
    await file.download_to_drive(file_path)

    # ✅ Detect file type and read it
    try:
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path, encoding="latin1")
        elif file_path.endswith((".xls", ".xlsx")):
            df = pd.read_excel(file_path)
        else:
            await update.message.reply_text("❌ Unsupported file format. Please send a CSV or Excel file.")
            return

        # ✅ Required columns
        required_columns = ["CALL ID", "CUSTOMER NAME", "CALL STAGE", "PENDING PARTS", "AGEING"]
        if not all(col in df.columns for col in required_columns):
            await update.message.reply_text("❌ Missing required columns in the file.")
            return

        # ✅ Convert AGEING column to numeric
        df["AGEING"] = pd.to_numeric(df["AGEING"], errors="coerce")

        # ✅ Filter calls where AGEING > 7
        df_filtered = df[df["AGEING"] > 7][required_columns]

        # ✅ Check if there are results
        if df_filtered.empty:
            await update.message.reply_text("✅ No pending calls found with AGEING > 7.")
            return

        # ✅ Limit to first 5 rows and format output
        preview = df_filtered.head(5).to_string(index=False)

        # ✅ Ensure message fits Telegram's 4096-character limit
        if len(preview) > 4000:
            preview = preview[:4000] + "\n\n(Truncated output...)"

        await update.message.reply_text(f"✅ Found {len(df_filtered)} calls with AGEING > 7.\n\n{preview}")

    except Exception as e:
        await update.message.reply_text(f"❌ Error processing the file: {e}")

# ✅ Create the bot application
def main():
    app = Application.builder().token(TOKEN).build()

    # ✅ Add command and message handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    # ✅ Run the bot
    print("🚀 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
