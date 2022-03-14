import sys
import time

import requests
import telegram

import app_logger
import settings
from validation import HWResponse, Tokens

logging = app_logger.get_logger(__name__)

PRACTICUM_TOKEN = settings.PRACTICUM_TOKEN
TELEGRAM_TOKEN = settings.TELEGRAM_TOKEN
TELEGRAM_CHAT_ID = settings.TELEGRAM_CHAT_ID


def send_message(bot, message):
    """Отправка сообщения в telegram."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logging.info(f'Бот отправил сообщение {message}')
    except Exception as error:
        logging.error(f'Бот не смог отправить сообщение по причине {error}')


def get_api_answer(current_timestamp):
    """Получение списка ДЗ, начиная со времени current_timestamp."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}

    hw_statuses = requests.get(
        url=settings.ENDPOINT,
        headers=settings.HEADERS,
        params=params
    )

    status_code = hw_statuses.status_code
    if status_code == requests.codes.ok:
        return hw_statuses.json()
    else:
        logging.error(f'Ресурс недоступен, причина: {hw_statuses.reason}')
        raise ValueError('Ответ не был получен')


def check_response(response):
    """Проверка ответа сервера.

    При ошибке выдаёт исключение. Если нет ошибок, возвращает список ДЗ
    """
    hw_response = HWResponse(response)
    return hw_response.check_response()


def parse_status(homework):
    """Возвращает строку с информацией о ДЗ и статусе её проверки."""
    homework_name = homework['homework_name']
    homework_status = homework['status']
    verdict = settings.HOMEWORK_STATUSES[homework_status]

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка токенов."""
    tokens = Tokens(PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)
    return tokens.check_tokens()


def main():
    """Основная логика работы бота."""
    if check_tokens():
        logging.info('Бот запущен')
    else:
        sys.exit()

    last_error_msg = ''
    bot = telegram.Bot(token=settings.TELEGRAM_TOKEN)

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
            time.sleep(settings.RETRY_TIME)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(message)
            if str(error) != last_error_msg:
                send_message(bot, message)
                last_error_msg = str(error)
            time.sleep(settings.RETRY_TIME)
        else:
            logging.info('Бот остановлен')


if __name__ == '__main__':
    main()
