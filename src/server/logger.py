import structlog
import logging
import logging.handlers
import os

# Получаем путь к текущей директории, где находится .py файл
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Поднимаемся на один уровень вверх
PROJECT_ROOT = os.path.dirname(os.path.dirname(CURRENT_DIR))

# Создаем путь к папке /logs в корневой директории проекта
LOG_DIR = os.path.join(PROJECT_ROOT, "logs")

# Создаем папку для логов, если её нет
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)


# Настройка structlog для логирования в консоль и в файл
def setup_logging():
    # Настройка structlog
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,  # Добавляет уровень логирования
            structlog.processors.StackInfoRenderer(),  # Добавляет информацию о стеке
            structlog.processors.TimeStamper(
                fmt="iso"
            ),  # Добавляет временную метку в формате iso
            structlog.processors.format_exc_info,  # Добавляет информацию об исключениях
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,  # Подготавливает данные для форматирования
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    main_logger = logging.getLogger()
    main_logger.setLevel(logging.INFO)

    # Обработчик для вывода в консоль
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            processor=structlog.dev.ConsoleRenderer(colors=True),
        )
    )

    # Путь к файлу логов
    log_file_path = os.path.join(LOG_DIR, "server.log")

    # Настройка logging для записи в файл
    file_handler = logging.handlers.RotatingFileHandler(
        log_file_path,
        maxBytes=1024 * 1024,
        backupCount=5,  # Логи ротируются при достижении 1 МБ
    )
    file_handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            processor=structlog.processors.JSONRenderer()
        )
    )

    main_logger.addHandler(console_handler)
    main_logger.addHandler(file_handler)


setup_logging()
LOGGER = structlog.get_logger()
