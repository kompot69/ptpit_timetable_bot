import telebot
import os
from dotenv import load_dotenv
load_dotenv(".env")
from chatIDs import chatIDs
bot = telebot.TeleBot(os.environ.get("TOKEN"))
print("Жду сообщение для рассылки...")
@bot.message_handler(content_types='text')
def notify(message):
    if message.from_user.id != 390623928:
        print('Кто-то написал в бота...')
        bot.send_message(message.from_user.id,  f'Бот обновляется...')
    else:
        print('Отправляю сообщения...')
        for id in chatIDs:
            try:
                bot.send_message(id,  message.text)
            except Exception as e:
                bot.send_message(390623928,  f"Ошибка отправки в чат "+id)
        return print('Сообщения отправлены')
if __name__ == "__main__":
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        pass
print("Выход...")
