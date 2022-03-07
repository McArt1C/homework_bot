import os
import time
from dotenv import load_dotenv
from http import HTTPStatus

import requests
import telegram

import app_logger

load_dotenv()

logging = app_logger.get_logger(__name__)

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 6
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    """Отправка сообщения в telegram"""

    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logging.info(f'Бот отправил сообщение {message}')
    except Exception as error:
        logging.error(f'Бот не смог отправить сообщение по причине {error}')


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
        logging.error('Ресурс недоступен')
        raise ValueError('Ответ не был получен')


def check_response(response):
    """Проверка ответа сервера.

    При ошибке выдаёт исключение. Если нет ошибок, возвращает список ДЗ
    """

    if type(response) != dict:
        error_msg = 'Ответ от API содержит некорректный тип.'
        logging.error(error_msg)
        raise TypeError(error_msg)
    elif 'current_date' and 'homeworks' not in response.keys():
        error_msg = 'В ответе API нет ожидаемых ключей.'
        logging.error(error_msg)
        raise ValueError(error_msg)
    elif type(response['homeworks']) != list:
        error_msg = 'Домашние задания не являются списком.'
        logging.error(error_msg)
        raise TypeError(error_msg)
    elif len(response['homeworks']) == 0:
        error_msg = 'В ответе от API нет новых домашних заданий.'
        logging.debug(error_msg)
        raise ValueError(error_msg)
    homeworks = response.get('homeworks')
    return homeworks


def parse_status(homework):
    """Возвращает строку с информацией о ДЗ и статусе её проверки"""

    homework_name = homework['homework_name']
    homework_status = homework['status']
    verdict = HOMEWORK_STATUSES[homework_status]

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

    if not check_tokens():
        logging.critical('Ошибка токена')
    else:
        logging.info('Бот запущен')

    last_error_msg = ''
    bot = telegram.Bot(token=TELEGRAM_TOKEN)

    while True:
        current_timestamp = int(time.time())
        try:
            logging.info('Бот делает запрос')
            response = get_api_answer(current_timestamp)
            homeworks_list = check_response(response)
            for homework in homeworks_list:
                logging.info(f'Бот получил результат {homework}')
                new_status = parse_status(homework)
                send_message(bot, new_status)
            time.sleep(RETRY_TIME)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(message)
            if str(error) != last_error_msg:
                send_message(bot, message)
                last_error_msg = str(error)
            time.sleep(RETRY_TIME)
        else:
            logging.info('Бот остановлен')


if __name__ == '__main__':
    main()
