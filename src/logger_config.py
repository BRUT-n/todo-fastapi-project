import logging.config
import sys
from logging import Formatter, StreamHandler

from pythonjsonlogger.json import JsonFormatter

from src.config import Environment, settings


def setup_logging():
    """Настраивает логирование под текущее окружение."""
    log_level = settings.app.LOG_LEVEL
    env = settings.app.ENVIRONMENT

    # 1. Определяем конфигурацию форматтера в зависимости от окружения
    if env == Environment.LOCAL:
        formatter_config = {
            "format": (
                "[%(asctime)s.%(msecs)03d] %(name)-25s [%(levelname)-7s] - %(message)s"
            ),
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
        formatter_class = Formatter
    elif env == Environment.TEST:
        formatter_config = {
            "format": "[%(levelname)s] %(name)s: %(message)s",
        }
        formatter_class = Formatter
    else:
        # Для продакшена (JSON)
        formatter_class = JsonFormatter
        formatter_config = {
            "fmt": "%(asctime)s %(levelname)s %(name)s %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "rename_fields": {
                "asctime": "timestamp_utc",
                "levelname": "level",
                "name": "logger",
            },
            "json_ensure_ascii": False,
        }

    # 2. Собираем единый конфиг для всей системы
    LOGGING_CONFIG = {
        "version": 1,
        # True сбросит дефолтные настройки uvicorn
        "disable_existing_loggers": False,
        "formatters": {
            "target_format": {
                "()": formatter_class,  # Динамически подставляем класс форматтера
                **formatter_config,  # распаковка настройки форматтера
            }
        },
        "handlers": {
            "console": {
                "class": StreamHandler,
                "stream": sys.stdout,  # Безопасное указание stdout для dictConfig
                "formatter": "target_format",
                "level": log_level,
            }
        },
        "loggers": {
            # Корневой логгер (ловит всё, включая ваши кастомные логи)
            "": {
                "handlers": ["console"],
                "level": log_level,
            },
            # Перехватываем uvicorn и отключаем дублирование (propagate: False)
            "uvicorn": {
                "handlers": ["console"],
                "level": log_level,
                "propagate": False,
            },
            "uvicorn.error": {
                "handlers": ["console"],
                "level": log_level,
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["console"],
                "level": log_level,  # можно "WARNING" чтобы не засорять логи
                "propagate": False,
            },
            # Перехватываем SQLAlchemy
            "sqlalchemy.engine": {
                "handlers": ["console"],
                "level": log_level,
                "propagate": False,
            },
        },
    }

    # 3. Применяем конфигурацию один раз для всего приложения
    logging.config.dictConfig(LOGGING_CONFIG)


# def setup_logging():
#     """Настраивает логирование под текущее окружение."""

#     # уровень логов, по авто-конфигу
#     log_level = settings.app.LOG_LEVEL

#     # обработчик для вывода в консоль (Docker читает консоль контейнера)
#     handler = StreamHandler(sys.stdout) # отправлять логи текстовый поток (stream)

#     # формат логов в зависимости от окружения
#     if settings.app.ENVIRONMENT == Environment.LOCAL:
#         # лкоально - удобный текстовый формат
#         formatter = Formatter(
#             fmt="[%(asctime)s.%(msecs)03d]
#               %(name)-25s [%(levelname)-7s] - %(message)s",
#             datefmt="%Y-%m-%d %H:%M:%S"
#         )
#     elif settings.app.ENVIRONMENT == Environment.TEST:
#         formatter = Formatter(
#             fmt="[%(levelname)s] %(name)s: %(message)s"
#         )
#     else:
#         # Перечисляем в fmt базовые поля, которые нужны
#         # Все поля из extra из middleware библиотека ДОБАВИТ САМА.
#         formatter = JsonFormatter(
#             fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
#             datefmt="%Y-%m-%d %H:%M:%S",
#             rename_fields={
#                 "asctime": "timestamp_utc",
#                 "levelname": "level",
#                 "name": "logger"
#                 },
#             json_ensure_ascii=False # Чтобы кириллица не превращалась в коды
#         )

#     # установка форматера для хендлера
#     handler.setFormatter(formatter)

#     # Применяем настройки к корневому логгеру
#     # остальные логгеры передают логи через него
#     root_logger = getLogger()
#     root_logger.setLevel(log_level) # установка логеру уровня логов

#     root_logger.handlers.clear()
#     root_logger.addHandler(handler)

#     # 2. Перехватываем логгеры Uvicorn и заставляем их использовать наш handler
#     uvicorn_loggers = (
#         "uvicorn",
#         "uvicorn.error",
#         "uvicorn.access",
#     )

#     for logger_name in uvicorn_loggers:
#         uvicorn_logger = getLogger(logger_name)
#         uvicorn_logger.handlers.clear()
#         uvicorn_logger.addHandler(handler)
#         uvicorn_logger.setLevel(log_level)
#         # Отключаем передачу логов выше (к дефолтному uvicorn-конфигу)
#         uvicorn_logger.propagate = False

#     # ПЕРЕХВАТЫВАЕМ ЛОГИ БАЗЫ ДАННЫХ (SQLAlchemy)
#     sql_logger = getLogger("sqlalchemy.engine")
#     sql_logger.handlers.clear()
#     sql_logger.addHandler(handler)
#     sql_logger.setLevel(log_level)
#     sql_logger.propagate = False
