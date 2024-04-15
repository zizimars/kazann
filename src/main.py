import datetime
import os
import sqlite3

import telebot
from telebot import types
from dotenv import load_dotenv
import pandas as pd

import db


load_dotenv()
TG_TOKEN = os.environ["TG_TOKEN"]
bot = telebot.TeleBot(token=TG_TOKEN, threaded=False)

db.init()

data = pd.read_csv(
    "data/khwtds.csv", dtype={"ID": int, "Image": str, "Description": str}
)


def get_unshown_images() -> pd.DataFrame:
    shown_images = db.get_all_unique_ids()
    unshown_images = data[~data["ID"].isin(shown_images)]
    return unshown_images


@bot.callback_query_handler(func=lambda _: True)
def callback_handler(call: types.CallbackQuery):
    user_name = call.from_user.username
    action, image_id = call.data.split("_")

    image_id = int(float(image_id))
    current_time = datetime.datetime.now()

    if action in ["yes", "DELETE"]:
        try:
            db.insert(
                user_name=user_name,
                id=image_id,
                answer=1 if action == "yes" else 0,
                annotation=None,
                time=current_time,
            )
            bot.send_message(
                chat_id=call.message.chat.id,
                text=f"{image_id} : \nЖауап сақталды. Рахмет!",
            )

        except sqlite3.IntegrityError:
            bot.send_message(
                chat_id=call.message.chat.id,
                text=f"{image_id} суретке бұрын жауап берілген. Келесі суретке көшеміз.",
            )
        finally:
            start(call.message)

    elif action == "no":
        ask_for_description(call.message, image_id, user_name)


@bot.message_handler(commands=["start"])
def start(message):
    unshown_images = get_unshown_images()
    if unshown_images.empty:
        bot.send_message(chat_id=message.chat.id, text="Аяқталды")
        return

    image = unshown_images.sample(frac=1).iloc[0]

    reply_markup = types.InlineKeyboardMarkup()
    yes_button = types.InlineKeyboardButton("Yes", callback_data=f'yes_{image["ID"]}')
    no_button = types.InlineKeyboardButton("No", callback_data=f'no_{image["ID"]}')
    delete_button = types.InlineKeyboardButton(
        "DELETE", callback_data=f'DELETE_{image["ID"]}'
    )
    reply_markup.add(yes_button, no_button, delete_button)

    if os.path.exists(image["Image"]):
        with open(image["Image"], "rb") as photo:
            bot.send_photo(
                chat_id=message.chat.id,
                photo=photo,
                caption=f'Сурет |{image["ID"]}|: \n{image["Description"]}',
                reply_markup=reply_markup,
            )
    # else:
    #     raise Exception("Missing the dataset")


def ask_for_description(message, image_id, user_name):
    msg = bot.send_message(
        chat_id=message.chat.id,
        text=f"{image_id}: \nЖаңа лейблді енгізіңіз. \nҚате енгізген жағдайда қайтадан No басыңыз",
    )
    bot.register_next_step_handler(msg, process_custom_description, image_id, user_name)


def process_custom_description(message: types.Message, image_id, user_name):
    if message.text is None:
        return

    custom_description = message.text
    user_name = message.from_user.username
    current_time = datetime.datetime.now()

    try:
        db.insert(
            user_name=user_name,
            id=image_id,
            answer=2,
            annotation=custom_description,
            time=current_time,
        )
    except sqlite3.IntegrityError:
        db.update(
            user_name=user_name,
            id=image_id,
            answer=2,
            annotation=custom_description,
            time=current_time,
        )
    finally:
        bot.send_message(
            chat_id=message.chat.id,
            text=f"{image_id}: \nЖаңа лейбл - ** {custom_description} **. Жауап бергеніңіз үшін Рақмет!",
        )
        start(message)


@bot.message_handler(commands=["stop"])
def handle_stop(message):
    bot.reply_to(
        message, "Келесі кездескенше! Қайтадан бастау үшін /start -ты басыңыз."
    )


@bot.message_handler(commands=["support"])
def handle_support(message):
    bot.reply_to(
        message,
        "Сәлем! Бұл боттың мақсаты — қазақша қолжазба датасетінің аннотацияларын тексеру. \nЕгер лейблдің сөзі суреттегі сөзге дәл сәйкес келсе, *Yes* батырмасын басыңыз;\nЕгер лейблдағы сөзде қате болса, онда *No* батырмасын басып, жаңа лейблді енгізіңіз.\nМіндетті түрде қазақша раскладкамен енгізіңіз.\nҚателер:\n     — фонетикалық/морфологиялық қате\n     — Бас/кіші қаріптің сәйкессіздігі\n     — 1-ден артық пунктуациялық символ ('.', ',', '?', '!', ':', ' '' ', ' ' пробел,'-',';', т.б)\n     — Сөз бен символдың арасында пробел бар ('балалар ,' ==> 'балалар,')\nЕгер: \n     — суретте 1-ден көп сөз болса;\n     — суреттегі сөзді оқу қиын болса;\n     — жауап беруге сенімді болмасыңыз\n     — тек латын әріптерден тұрса (EXPO, US, etc)\nонда *DELETE* батырмасын басыңыз.\n\nСұрақтарыңыз болған жағдайда, маған (https://t.me/zizzimars) немесе (https://t.me/asociallized)-ке жазуыңызды сұраймыз.",
    )


def main():
    print("Starting...")
    bot.polling(non_stop=True)


if __name__ == "__main__":
    main()
