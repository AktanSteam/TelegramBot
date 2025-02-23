import logging

import re

from telegram import Update

from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

from openai import OpenAI



# Ваш ключ API для OpenRouter

OPENROUTER_API_KEY = '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'



# Инициализация клиента OpenRouter

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=OPENROUTER_API_KEY)



async def start(update: Update, context: CallbackContext):

    # Отправка приветственного сообщения при старте бота.

    await update.message.reply_text("Привет! Напиши мне что-нибудь, и я постараюсь ответить.", parse_mode='Markdown')



async def handle_message(update: Update, context: CallbackContext):

    # Обработка сообщений от пользователей и взаимодействие с нейросетью.

    user_message = update.message.text  # Получаем текст от пользователя

    logging.info(f"Получено сообщение от пользователя: {user_message}")



    try:

        # Отправка запроса к нейросети

        completion = client.chat.completions.create(

            model="deepseek/deepseek-r1:free", # Модель которую будет использоваться

            messages=[{"role": "user", "content": user_message}]

        )



        # Логирование ответа от нейросети

        logging.info(f"Ответ от нейросети: {completion}")



        # Проверка и обработка ответа

        if completion and hasattr(completion, 'choices') and completion.choices:

            choice = completion.choices[0]

            content = choice.message.content

            cleaned_content = re.sub(r'<.*?>', '', content).strip()  # Убираем теги



            if cleaned_content:

                bot_response = f"*Ответ от нейросети:*\n\n{cleaned_content}"

            else:

                bot_response = "*Ответ от нейросети не содержит нужной информации.*"

                logging.error("Ответ от нейросети пустой.")

        else:

            bot_response = "*Извините, я не получил корректный ответ от нейросети. Пожалуйста, попробуйте позже.*"



    except Exception as e:

        bot_response = f"*Произошла ошибка:* {str(e)}"

        logging.error(f"Ошибка при обработке сообщения: {str(e)}")



    logging.info(f"Отправка сообщения пользователю: {bot_response}")

    await update.message.reply_text(bot_response, parse_mode='Markdown')



def main():

    """Основная функция для запуска бота."""

    # Включение логирования для отслеживания ошибок

    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)



    TELEGRAM_TOKEN = '7561462930:AAESoDgJdy5wik0gLNAlGE4ktazuVBk8ttY'



    # Инициализация приложения

    application = Application.builder().token(TELEGRAM_TOKEN).build()



    # Обработчики команд и сообщений

    application.add_handler(CommandHandler("start", start))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))



    # Запуск бота

    application.run_polling()



if __name__ == '__main__':

    main()

