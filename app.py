import logging
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
import keys
import my_functions

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send welcome message."""
    user = update.message.from_user

    logger.info("User %s just started the bot.", user.first_name)

    await context.bot.send_message(
        chat_id=user.id,
        text="Hello. This bot is my test task from Anastasia. "
             "I was asked to create a parser to get exchange rate of USD against UAH. "
             "Please, use command /get_exchange_rate to receive .xlsx file with recent currency insights.\n\n"
             "For the convenience of demonstration, the parsing interval will be 1 minute instead of 1 hour.\n\n"
             "Thank you, guys, for the opportunity!"
    )


async def get_exchange_rate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Returns to user an exchange rate of USD against UAH."""
    user = update.message.from_user

    logger.info("User %s just requested exchange rate of USD-UAH.", user.first_name)
    my_functions.create_excel_file()

    await context.bot.send_document(
        chat_id=user.id,
        document=open('USD-UAH exchange rates.xlsx', 'rb'),
        caption='Here is your Exel table with the last exchange rates of USD-UAH.'
    )


async def handle_other_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Returns to user an exchange rate of USD against UAH."""
    user = update.message.from_user

    logger.info("User %s sent a message other than /get_exchange_rate command.", user.first_name)

    await context.bot.send_message(chat_id=user.id, text="I can only handle /get_exchange_rate and /start commands.")


def main() -> None:
    """Run the bot."""
    # Create the application
    application = Application.builder().token(keys.TEST_API_TOKEN).build()

    # Create command handler
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("get_exchange_rate", get_exchange_rate))
    application.add_handler(MessageHandler(filters.ALL & ~filters.Regex(r'^/get_exchange_rate'), handle_other_messages))

    # Schedule the job to run every hour
    application.job_queue.run_repeating(my_functions.parse_exchange_rate_and_store, interval=60.0, first=1.0)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()