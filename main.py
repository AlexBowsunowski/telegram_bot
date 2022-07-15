import telebot 
from telebot import types
from telegram_bot import config as cfg
from telegram_bot.database import Planner 
from telegram_bot import exceptions as ex

print(cfg.TOKEN)
bot = telebot.TeleBot(cfg.TOKEN)
planner = Planner()


@bot.message_handler(commands=['start'])
def send_keyboard(message, text="Привет, чем я могу тебе помочь?"):
    keyboard = types.ReplyKeyboardMarkup(row_width=2)
    add_button = types.KeyboardButton(cfg.ADD_BUTTON)
    show_button = types.KeyboardButton(cfg.SHOW_BUTTON)
    delete_button = types.KeyboardButton(cfg.DELETE_BUTTON)
    delete_all_button = types.KeyboardButton(cfg.DELETE_ALL_BUTTON)
    keyboard.add(add_button, show_button)
    keyboard.add(delete_button, delete_all_button)

    message = bot.send_message(
        message.from_user.id,
        text=text, 
        reply_markup=keyboard,
    )

    bot.register_next_step_handler(message, callback)


def callback(message):
    if message.text == cfg.ADD_BUTTON:
        message = bot.send_message(
            chat_id=message.chat.id,
            text="Давайте добавим дело. Напиши его в чат."
        )
        bot.register_next_step_handler(message, add)
    elif message.text == cfg.SHOW_BUTTON:
        show(message=message)
    elif message.text == cfg.DELETE_BUTTON:
        try:
            tasks = planner.get_tasks()
            keyboard = typed.ReplyKeyboardMarkup(row_width=2)
            for task in tasks:
                task_button = types.KeyboardButton(task)
                keyboard.add(task_button)
            bot.send_message(
                chat_id=message.chat.id,
                text="Выбери задачу для удаления:",
                reply_markup=keyboard,
            )

            bot.register_next_step_handler(msg, delete)
        except ex.TasksNotExists:
            bot.send_message(
            chat_id=message.chat.id,
            text="Задач пока нет",
        )
        finally:
            send_keyboard(message=message, text="Чем еще могу помочь?")


    elif message.text == cfg.DELETE_ALL_BUTTON:
        delete_all(message=message) 


def add(message):
    planner.add(message=message)
    bot.send_message(
        chat_id=message.chat.id,
        text="Дело записано!"
    )
    send_keyboard(
        message=message,
        text="Чем я могу помочь?"
    )


def show(message):
    try:
        tasks: str = planner.show(message=message)
        bot.send_message(
            chat_id=message.chat.id,
            text=tasks,
        )
    except ex.TaskNotExists:
        bot.send_message(
            chat_id=message.chat.id,
            text="Задач пока нет",
        )
    finally:
        send_keyboard(message=message, text="Чем еще могу помочь?")


def delete(message):
    planner.delete(message=message)
    bot.send_message(
        chat_id=message.chat.id,
        text=f"Задача {message.text} удалена."
    )
    send_keyboard(message=message, text="Чем еще могу помочь?")

def delete_all(message):
    planner.delete_all(message=message)
    bot.send_message(
        chat_id=message.chat.id,
        text=f"Все задачи удалены."
    )
    send_keyboard(message=message, text="Чем еще могу помочь?")



if __name__ == '__main__':
    bot.infinity_polling()