from dataclasses import dataclass

import app_logger

logging = app_logger.get_logger(__name__)


@dataclass
class Tokens:
    """Содержит в себе токены и логику работы с ними."""

    practicum_token: str
    telegram_token: str
    telegram_chat_id: int

    def check_tokens(self):
        """Проверка токенов."""
        all_tokens = [
            self.practicum_token,
            self.telegram_token,
            self.telegram_chat_id,
        ]
        if all(all_tokens):
            return True
        logging.critical('Ошибка токена')
        return False


@dataclass
class HWResponse:
    """Датакласс для проверки результата запроса к API."""

    response: dict

    def check_response(self):
        """Проверка ответа сервера.

        При ошибке выдаёт исключение. Если нет ошибок, возвращает список ДЗ
        """
        if type(self.response) != dict:
            error_msg = 'Ответ от API содержит некорректный тип.'
            logging.error(error_msg)
            raise TypeError(error_msg)
        elif 'current_date' and 'homeworks' not in self.response.keys():
            error_msg = 'В ответе API нет ожидаемых ключей.'
            logging.error(error_msg)
            raise ValueError(error_msg)
        elif type(self.response.get('homeworks')) != list:
            error_msg = 'Домашние задания не являются списком.'
            logging.error(error_msg)
            raise TypeError(error_msg)
        elif not self.response.get('homeworks'):
            error_msg = 'В ответе от API нет новых домашних заданий.'
            logging.debug(error_msg)
            raise ValueError(error_msg)
        homeworks = self.response.get('homeworks')
        return homeworks
