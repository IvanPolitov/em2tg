import os

import schedule
import telebot
import threading
import time
from imbox import Imbox
from telebot import types
from imaplib import IMAP4

TOKEN = os.getenv('tg_token')
bot = telebot.TeleBot(TOKEN)

commands = {
    'start'         : 'Это старт',
    'help'          : 'Список команд',
    'me'            : 'Данные пользователя',
    'check'         : 'Проверить новые сообщения',
    'login'         : 'Ввести данные',
    'logout'        : 'Удалить данные',
    'go'            : 'Начать уведомлять о новых сообщениях',
    'stop'          : 'Остановить уведомления',
}

users_data = dict()

class User:
    def __init__(self, name):
        self.name = name
        self.email = None
        self.email_server = None
        self.password = None
        self.unread_message_data = dict()

@bot.message_handler(commands=['start'])        # приветствие
def start(message: types.Message):
    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton("Yes", callback_data="cb_yes")
    button2 = types.InlineKeyboardButton("No", callback_data="cb_no")
    markup.add(button1)
    markup.add(button2)
    bot.send_message(message.chat.id, '''
    Привет, Это мой бот для чтения электронных писем. 
Для использования потребуется заполнить адрес электронной почт, используемый почтовый сервер и 
пароль для внешних приложений. Напишите /help для того, чтобы узнать команды.
                                      ''', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call: types.CallbackQuery):
    del_mail(call.data, call.message.chat.id)
    bot.send_message(call.message.chat.id, str(call.data) + ' удалено')

def del_mail(uid, chat_id):
    with Imbox(
            users_data[chat_id].email_server,
            username=users_data[chat_id].email,
            password=users_data[chat_id].password,
            ssl=True,
            ssl_context=None,
            starttls=False) as imbox:
        imbox.delete((uid[2:-1]).encode('utf8'))

@bot.message_handler(commands=['login'])        # заполнение данных текущего юзера
def login(message: types.Message):
    bot.send_message(message.chat.id, 'Как тебя зовут?')
    bot.register_next_step_handler(message, get_name)

def get_name(message: types.Message):
    if message.text == '/start':
        start(message)
    else:
        try:
            chat_id = message.chat.id
            name = message.text
            user = User(name)
            users_data[chat_id] = user
            bot.send_message(chat_id, 'Твой IMAP сервер?')
            bot.register_next_step_handler(message, get_serv)
        except Exception as e:
            bot.reply_to(message, 'Давай по новой, Миша')

def get_serv(message: types.Message):
    if message.text == '/start':
        start(message)
    else:
        try:
            chat_id = message.chat.id
            user = users_data[chat_id]
            if message.text.split('.')[0] != 'imap':
                bot.send_message(chat_id, 'Это точно не imap')
                get_name(message)
            elif message.text.split('.')[-1] not in ["ru", "com"]:
                bot.send_message(chat_id, 'Неправильный домен')
                get_name(message)
            else:
                user.email_server = message.text
                bot.send_message(chat_id, 'Твоя электронная почта?')
                bot.register_next_step_handler(message, get_email)
        except Exception as e:
            bot.reply_to(message, 'Давай по новой, Миша')

def get_email(message: types.Message):
    if message.text == '/start':
        start(message)
    else:
        try:
            chat_id = message.chat.id
            user = users_data[chat_id]
            if len(message.text.split('@')) != 2:
                bot.send_message(chat_id, 'Это не электронная почта')
                get_serv(message)
            elif message.text.split('.')[-1] not in ["ru", "com"]:
                bot.send_message(chat_id, 'Неправильный домен')
                get_serv(message)
            else:
                user.email = message.text
                bot.send_message(chat_id, 'Пароль для внешних приложений?')
                bot.register_next_step_handler(message, get_pass)
        except Exception as e:
            bot.reply_to(message, 'Давай по новой, Миша')

def get_pass(message: types.Message):
    if message.text == '/start':
        start(message)
    else:
        try:
            chat_id = message.chat.id
            user = users_data[chat_id]
            user.password = message.text
            bot.send_message(message.chat.id, 'Привет, ' + users_data[chat_id].name + ', твоя почта: ' + users_data[chat_id].email)
        except Exception as e:
            bot.reply_to(message, 'Давай по новой, Миша')

@bot.message_handler(commands=['logout'])       # удаление данных текущего юзера
def logout(message: types.Message):
    chat_id = message.chat.id
    try:
        del users_data[chat_id]
        bot.send_message(chat_id, 'Со смертью этого персонажа нить вашей судьбы обрывается')
    except Exception as e:
        bot.send_message(chat_id, 'Тебя никогда не существовало')

@bot.message_handler(commands=['me'])       # данные текущего юзера
def command_me(message: types.Message):
    try:
        chat_id = message.chat.id
        help_text = 'Ты ' + \
                    users_data[chat_id].name + ': \n' + \
                    users_data[chat_id].email + '\n' + \
                    users_data[chat_id].email_server + '\n' + \
                    users_data[chat_id].password
        bot.send_message(message.chat.id, help_text)
    except Exception as e:
        bot.reply_to(message, 'Тебя никогда не существовало')

@bot.message_handler(commands=['help'])       # возможные команды
def command_help(message: types.Message):
    help_text = "Список команд: \n"
    for key in commands:
        help_text += '/' + key + ': ' + commands[key] + '\n'
    bot.send_message(message.chat.id, help_text)

@bot.message_handler(commands=['check'])       # проверка
def command_check(message: types.Message):
    qqq = list(check_mail(message))
    bot.send_message(message.chat.id, 'Пожалуйста, подождите')
    try:
        if qqq:
            for i in qqq:
                markup = types.InlineKeyboardMarkup()
                mail_text = 'UID сообщения ' + str(i[0]) + '\n'
                mail_text += 'Имя отправителя: ' + str(i[1][0]) + '\n'
                mail_text += 'Адрес отправителя: ' + str(i[1][1]) + '\n'
                mail_text += 'Тема сообщения: ' + str(i[1][2]) + '\n'
                mail_text += 'Текст: ' + '\n' + str(i[1][3]) + '\n'
                button1 = types.InlineKeyboardButton("Удалить", callback_data=str(i[0]))
                markup.add(button1)
                bot.send_message(message.chat.id, mail_text, reply_markup=markup)
            bot.send_message(message.chat.id, 'На данный момент всё')
        else:
            bot.send_message(message.chat.id, 'Полковнику никто не пишет')
    except:
        bot.send_message(message.chat.id, 'Полковнику никто не пишет. Совсем.')


@bot.message_handler(commands=['go'])
def command_go(message: types.Message):
    if message.chat.id in users_data:
        schedule.every(10).seconds.do(check_mail_permanently, message=message)
        bot.send_message(message.chat.id, 'Запущена проверка новых сообщений. Вам будут приходить уведомления')
    else:
        bot.send_message(message.chat.id, 'Тебя никогда не существовало')

@bot.message_handler(commands=['stop'])
def command_stop(message: types.Message):
    bot.send_message(message.chat.id, 'Уведомления о новых сообщениях отключены')
    schedule.clear()

def check_mail_permanently(message: types.Message):
    chat_id = message.chat.id
    with Imbox(
            users_data[chat_id].email_server,
            username=users_data[chat_id].email,
            password=users_data[chat_id].password,
            ssl=True,
            ssl_context=None,
            starttls=False) as imbox:
        all_inbox_messages = imbox.messages(unread=True)
        mail_dict = dict()
        user_message_ids = users_data[chat_id].unread_message_data.keys()
        for uid, mail_message in all_inbox_messages:
            if 'subject' not in mail_message.keys():
                mail_message.subject = '<Без темы>'
            mail_dict[uid] = (mail_message.sent_from[0]["name"],
                              mail_message.sent_from[0]["email"],
                              mail_message.subject,)
            if uid not in user_message_ids:
                users_data[chat_id].unread_message_data[uid] = mail_dict[uid]
                mail_text = 'UID сообщения ' + str(uid) + '\n'
                mail_text += 'Имя отправителя: ' + str(mail_dict[uid][0]) + '\n'
                mail_text += 'Адрес отправителя: ' + str(mail_dict[uid][1]) + '\n'
                mail_text += 'Тема сообщения: ' + str(mail_dict[uid][2]) + '\n'
                bot.send_message(message.chat.id, mail_text)
        for key in user_message_ids:
            if key not in mail_dict.keys():
                del users_data[chat_id].unread_message_data[key]

@bot.message_handler(func=lambda m: True)       # обработка неверной команды
def echo_all(message: types.Message):
    bot.reply_to(message, 'Извини, в ответах я ограничен, правильно задавай вопросы')

# функция чтения эмейла
def check_mail(message: types.Message):
    try:
        chat_id = message.chat.id
        with Imbox(
                users_data[chat_id].email_server,
                username=users_data[chat_id].email,
                password=users_data[chat_id].password,
                ssl=True,
                ssl_context=None,
                starttls=False) as imbox:
            all_inbox_messages = imbox.messages(unread=True)
            mail_dict = dict()
            for uid, mail_message in all_inbox_messages:
                if 'subject' not in mail_message.keys():
                    mail_message.subject = '<Без темы>'
                if (not mail_message.body["plain"] and mail_message.body["html"]):
                    mail_dict[uid] = (mail_message.sent_from[0]["name"],
                                      mail_message.sent_from[0]["email"],
                                      mail_message.subject,
                                      '<HTML страничка>')
                elif not mail_message.body["plain"][0]:
                    mail_dict[uid] = (mail_message.sent_from[0]["name"],
                                mail_message.sent_from[0]["email"],
                                mail_message.subject,
                                "<Без текста>")
                elif mail_message.body["plain"][0].split()[0] in ['<html>', '<!doctype']:
                    mail_dict[uid] = (mail_message.sent_from[0]["name"],
                                      mail_message.sent_from[0]["email"],
                                      mail_message.subject,
                                      '<HTML страничка>')
                else:
                        mail_dict[uid] = (mail_message.sent_from[0]["name"],
                                    mail_message.sent_from[0]["email"],
                                    mail_message.subject,
                                    mail_message.body["plain"][0][:4000])
                imbox.mark_seen(uid)

            for i in mail_dict:
                yield (i, mail_dict[i])
    except IMAP4.abort:
        pass
    except KeyError:
        bot.send_message(message.chat.id, 'Кто ты, воин?')


if __name__ == '__main__':
    bot.enable_save_next_step_handlers(delay=2)
    bot.load_next_step_handlers()
    threading.Thread(target=bot.infinity_polling, name='bot_infinity_polling', daemon=True).start()
    while True:
        schedule.run_pending()
        time.sleep(1)
