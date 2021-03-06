import telebot
import pycountry
import requests
from functools import wraps
from telebot import types
import datetime
import time
import string
import os

bot = telebot.TeleBot(os.getenv("TELEGRAM_BOT_KEY"))
BASE_URL = "http://api.coronatracker.com/v3"


def get_status_by_country_name(country):
    try:
        country_code = pycountry.countries.get(name=country).alpha_2
        if country_code:
            r = requests.get(f'{BASE_URL}/v3/stats/worldometer/country?countryCode={country_code}')
            return r.json()[0]
        else:
            return False
    except Exception as error:
        print('Error: ' + repr(error))
        return False


def get_world_status():
    try:
        r = requests.get(f'{BASE_URL}/stats/worldometer/global')
        return r.json()
    except Exception as error:
        print('Error: ' + repr(error))
        return False


def get_recovered_percent(recovered, deaths):
    return round(recovered * 100 / (deaths + recovered), 2)


def get_deaths_percent(recovered, deaths):
    return round(deaths * 100 / (deaths + recovered), 2)


def get_active_cases_percent(active, confirmed):
    return round(active * 100 / confirmed, 2)


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton('Armenia')
    btn2 = types.KeyboardButton('World')
    markup.add(btn1, btn2)
    message_text = f"Ողջույն <b>{message.from_user.first_name}</b>! Կորոնավիրուսի մասին վերջին տվյալները ստանալու համար ուղարկեք երկրի անունը (լատինատառերով), օրինակ՝ Armenia, Russia, Italy, Iran և այլն։"
    bot.send_message(message.chat.id, message_text, parse_mode='html', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def mess(message):
    get_message = string.capwords(message.text.strip())
    if get_message == "World":
        data = get_world_status()
        reply_message = "Տվյալներ չեն գտնվել!"
        if data:
            reply_message = f"COVID-19-ի վերջին տվյալները Աշխարհում։ Աշխարհում կա <b>{data['totalConfirmed']}</b> վարակված անձ որոնցից ապաքինվել է <b>{data['totalRecovered']}({get_recovered_percent(data['totalRecovered'], data['totalDeaths'])}%)</b> մարդ, մահացել <b>{data['totalDeaths']}({get_deaths_percent(data['totalRecovered'], data['totalDeaths'])}%)</b>-ը և այժմ բուժում է ստանում <b>{data['totalActiveCases']}({get_active_cases_percent(data['totalActiveCases'], data['totalConfirmed'])}%)</b> մարդ։ Վերջին մեկ օրում գրանցվել է <b>{data['totalNewCases']}</b> նոր դեպք, մահացել է <b>{data['totalNewDeaths']}</b> մարդ։ Վարակվածների թվի տոկոսային աճը՝ <b>{round((data['totalNewCases'] / (data['totalConfirmed'] - data['totalNewCases'])) * 100, 2)}%</b>"
        bot.send_message(message.chat.id, reply_message, parse_mode='html')
    else:
        data = get_status_by_country_name(get_message)
        reply_message = "Երկրի անունը սխալ է, կամ տվյալներ չեն գտնվել!"
        if data:
            reply_message = f"COVID-19-ի վերջին տվյալները <b>{data['country']}</b>-ում։ Երկրում կա <b>{data['totalConfirmed']}</b> վարակված անձ որոնցից ապաքինվել է <b>{data['totalRecovered']}({get_recovered_percent(data['totalRecovered'], data['totalDeaths'])}%)</b> մարդ, մահացել <b>{data['totalDeaths']}({get_deaths_percent(data['totalRecovered'], data['totalDeaths'])}%)</b>-ը և այժմ բուժում է ստանում <b>{data['activeCases']}({get_active_cases_percent(data['activeCases'], data['totalConfirmed'])}%)</b> մարդ։ Վերջին մեկ օրում գրանցվել է <b>{data['dailyConfirmed']}</b> նոր դեպք, մահացել է <b>{data['dailyDeaths']}</b> մարդ։ Յուրաքանչյուր մեկ միլիոն բնակչից վարակվել է <b>{data['totalConfirmedPerMillionPopulation']}</b> մարդ, մահացել <b>{data['totalDeathsPerMillionPopulation']}</b>-ը։ Վարակվածների թվի տոկոսային աճը՝ <b>{round((data['dailyConfirmed'] / (data['totalConfirmed'] - data['dailyConfirmed'])) * 100, 2)}%</b>"
        bot.send_message(message.chat.id, reply_message, parse_mode='html')


bot.polling(none_stop=True)
