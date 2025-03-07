from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import subprocess
import structlog
import logging
import logging.handlers
import os

# Получаем путь к текущей директории, где находится .py файл
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Поднимаемся на один уровень вверх
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

# Создаем путь к папке /logs в корневой директории проекта
LOG_DIR = os.path.join(PROJECT_ROOT, "logs")

# Создаем папку для логов, если её нет
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Настройка structlog для логирования в консоль и в файл
def setup_logging():
    # Путь к файлу логов
    log_file_path = os.path.join(LOG_DIR, "server.log")

    # Настройка logging для записи в файл
    file_handler = logging.handlers.RotatingFileHandler(
        log_file_path, maxBytes=1024 * 1024, backupCount=5  # Логи ротируются при достижении 1 МБ
    )
    file_handler.setFormatter(logging.Formatter("%(message)s"))
    file_handler.setLevel(logging.INFO)

    # Настройка structlog
    structlog.configure(
        processors=[
            structlog.processors.add_log_level,  # Добавляет уровень логирования
            structlog.processors.StackInfoRenderer(),  # Добавляет информацию о стеке
            structlog.dev.ConsoleRenderer(),  # Логирование в консоль
            structlog.processors.JSONRenderer(),  # Логирование в JSON
        ],
        logger_factory=structlog.PrintLoggerFactory(),
        wrapper_class=structlog.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Добавляем file_handler в logging
    logging.basicConfig(
        level=logging.INFO,
        handlers=[file_handler],
    )

setup_logging()
logger = structlog.get_logger()

class CalculatorHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Логируем GET-запрос
        logger.info("GET request received", path=self.path)

        if self.path == '/':
            # Возвращаем простое сообщение для корневого пути
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"Calculator API is running. Use POST /calc to evaluate expressions.")
            logger.info("GET response sent", status=200, path=self.path)
        else:
            # Для всех остальных GET-запросов возвращаем 404
            self.send_response(404)
            self.end_headers()
            logger.warning("Path not found", path=self.path, status=404)

    def do_POST(self):
        # Логируем начало обработки POST-запроса
        logger.info("POST request received", path=self.path)

        # Разделяем путь и query-параметры
        path = self.path.split('?')[0]

        if path == '/calc':
            try:
                # Получаем длину данных
                length = int(self.headers['Content-Length'])
                # Читаем данные
                post_data = self.rfile.read(length)
                # Парсим JSON
                data = json.loads(post_data)
                expression = data.strip()

                # Логируем полученное выражение
                logger.info("Expression received", expression=expression)

                # Получаем значение параметра float из query
                float_mode = self.get_float_mode()

                # Вызываем внешний калькулятор с учетом флага --float
                result = self.call_calculator(expression, float_mode)

                # Проверяем, является ли результат числом
                if self.is_number(result):
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"result": result}).encode())
                    logger.info("POST response sent", status=200, result=result)
                else:
                    # Если результат не число, считаем это ошибкой
                    self.send_response(500)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": result}).encode())
                    logger.error("Error occurred", status=500, error=result)

            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
                logger.error("Error occurred", status=500, error=str(e))
        else:
            self.send_response(404)
            self.end_headers()
            logger.warning("Path not found", path=self.path, status=404)

    def get_float_mode(self):
        # Парсим query-параметры
        query = self.path.split('?')
        if len(query) > 1:
            params = query[1].split('&')
            for param in params:
                if param.startswith('float='):
                    return param.split('=')[1].lower() == 'true'
        return False

    def call_calculator(self, expression, float_mode):
        # Вызываем внешний калькулятор (например, app.exe или main.c)
        try:
            # Формируем команду для запуска калькулятора
            command = ["build/app.exe"]
            if float_mode:
                command.append("--float")

            # Запускаем процесс и передаем выражение
            process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            stdout, stderr = process.communicate(input=expression)

            # Логируем вывод калькулятора
            logger.info("Calculator output", stdout=stdout, stderr=stderr)

            # Если есть stderr, считаем это ошибкой
            if stderr:
                return stderr.strip()
            return stdout.strip()

        except Exception as e:
            logger.error("Calculator call failed", error=str(e))
            return str(e)

    def is_number(self, s):
        # Проверяем, является ли строка числом (int или float)
        try:
            float(s)  # Пробуем преобразовать в float
            return True
        except ValueError:
            return False

def run(server_class=HTTPServer, handler_class=CalculatorHandler, port=8080):
    server_address = ('127.0.0.1', port)
    httpd = server_class(server_address, handler_class)
    logger.info("Starting server", port=port)
    httpd.serve_forever()

if __name__ == "__main__":
    run()