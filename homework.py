from dotenv import load_dotenv
from http import HTTPStatus
import logging
import os
import time

import requests
import telegram

# from telegram import ReplyKeyboardMarkup
# from telegram.ext import Updater, CommandHandler

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

REQUESTS_TIME_INTERVAL = 10 * 60


def send_message(bot, message):
    """Отправка сообщения"""
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)


def get_api_answer(current_timestamp):
    """Получение списка ДЗ, начиная со времени current_timestamp"""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}

    homework_statuses = requests.get(
        url=ENDPOINT,
        headers=HEADERS,
        params=params
    )

    if homework_statuses.status_code == HTTPStatus.OK:
        return homework_statuses.json()
    else:
        raise ValueError


def check_response(response):
    """Проверка ответа сервера"""
    if type(response) != dict:
        logging.error(stack_info=True)
        raise TypeError('Ответ от API содержит некорректный тип.')
    elif 'current_date' and 'homeworks' not in response.keys():
        logging.error(stack_info=True)
        raise ValueError('В ответе API нет ожидаемых ключей.')
    elif type(response['homeworks']) != list:
        logging.error(stack_info=True)
        raise TypeError('Домашние задания не являются списком.')
    elif len(response['homeworks']) == 0:
        logging.debug(exc_info=True)
        raise ValueError('В ответе от API нет новых домашних заданий.')
    homework = response.get('homeworks')
    return homework


def parse_status(homework):
    homework_name = homework['homework_name']
    homework_status = homework['status']

    ...

    verdict = HOMEWORK_STATUSES[homework_status]

    ...

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка токенов."""
    tokens = [PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]
    for token in tokens:
        if token is None:
            return False
    return True


def main():
    """Основная логика работы бота."""
    answer = get_api_answer(1)
    result = check_response(answer)
    print(result)
    return None

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    ...

    while True:
        try:
            response = ...

            ...

            current_timestamp = ...
            time.sleep(RETRY_TIME)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            ...
            time.sleep(RETRY_TIME)
        else:
            ...


if __name__ == '__main__':
    main()
