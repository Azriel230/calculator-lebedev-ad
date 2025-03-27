from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import subprocess

from logger import LOGGER

logger = LOGGER

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

                # Обрабатываем данные в зависимости от их типа
                if isinstance(data, dict):  # Если данные — это словарь
                    expression = data.get("expression", "").strip()  # Извлекаем выражение из словаря
                elif isinstance(data, str):  # Если данные — это строка
                    expression = data.strip()  # Используем строку как есть
                else:
                    raise ValueError("Invalid data type. Expected string or dictionary.")

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
