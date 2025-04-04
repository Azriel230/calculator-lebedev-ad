import sys
import requests
import time
import queue
import socket
import os
import json
from PySide6.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton, 
                              QCheckBox, QLineEdit, QVBoxLayout, QHBoxLayout, 
                              QWidget, QStatusBar, QTableWidget, QTableWidgetItem,
                              QHeaderView, QGraphicsOpacityEffect, QSizePolicy)
from PySide6.QtGui import (QRegularExpressionValidator, QFont,
                          QColor, QPainter, QIcon)
from PySide6.QtCore import (QRegularExpression, Qt, QPropertyAnimation, QDateTime,
                           QEasingCurve, Property, QObject, QThread, Signal, QTimer)

from dotenv import load_dotenv

load_dotenv("./.env")
HOST = os.getenv("SERVERHOST", "127.0.0.1")
PORT = os.getenv("SERVERPORT", 65432)

class StatusIndicator(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._color = QColor(128, 128, 128)
        self._radius = 5
        
        # Настройка анимации радиуса
        self._animation = QPropertyAnimation(self, b"radius")
        self._animation.setDuration(2000)  # Увеличили длительность для более плавного эффекта
        self._animation.setLoopCount(-1)
        self._animation.setEasingCurve(QEasingCurve.InOutSine)
        
        # Анимация
        self._animation.setKeyValueAt(0.0, 5)    # Начало
        self._animation.setKeyValueAt(0.25, 6)   # Первый пик
        self._animation.setKeyValueAt(0.5, 7)    # Основной пик
        self._animation.setKeyValueAt(0.75, 6)   # Спад
        self._animation.setKeyValueAt(1.0, 5)    # Возврат к началу

        # Анимация прозрачности с 5 шагами
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        
        self.opacity_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.opacity_anim.setDuration(3000)
        self.opacity_anim.setLoopCount(-1)
        self.opacity_anim.setEasingCurve(QEasingCurve.InOutSine)
        
        # Синхронизированная 5-шаговая анимация прозрачности
        self.opacity_anim.setKeyValueAt(0.0, 0.7)
        self.opacity_anim.setKeyValueAt(0.25, 0.85)
        self.opacity_anim.setKeyValueAt(0.5, 1.0)
        self.opacity_anim.setKeyValueAt(0.75, 0.85)
        self.opacity_anim.setKeyValueAt(1.0, 0.7)
        
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(self._color)
        painter.setPen(Qt.NoPen)
        
        center = self.rect().center()
        painter.drawEllipse(center, self._radius, self._radius)
        
        
    def start_animation(self):
        self._animation.start()
        self.opacity_anim.start()


    def stop_animation(self):
        self._animation.stop()
        self.opacity_anim.stop()
        self._radius = 5
        self.opacity_effect.setOpacity(1.0)
        self.update()
        
        
    def get_radius(self):
        return self._radius
        
        
    def set_radius(self, r):
        self._radius = r
        self.update()
        
        
    def set_color(self, color):
        self._color = color
        self.update()
        
        
    radius = Property(int, get_radius, set_radius)
    
    
class ServerStatusWorker(QObject):
    status_updated = Signal(int, str, str)  # code, text, error
    def __init__(self):
        super().__init__()
        self._active = True
        self.check_interval = 5000 #через сколько отправлять запрос
        self.current_time = 4000


    def run(self):
        while self._active:
            if self.current_time > self.check_interval:
                self.current_time = 0
                try:
                    response = requests.get("http://127.0.0.1:8080/", timeout=2)
                    if response.status_code == 200:
                        self.status_updated.emit(200, "Сервер доступен", "")
                    else:
                        self.status_updated.emit(
                            response.status_code, 
                            "Ошибка сервера", 
                            f"HTTP {response.status_code}"
                        )
                except Exception as e:
                    self.status_updated.emit(500, "Сервер недоступен", str(e))
            else:
                time.sleep(0.050)
                self.current_time = self.current_time + 50


    def stop(self):
        self._active = False


class CalculationWorker(QObject):
    calculation_finished = Signal(bool, str, str)
    history_updated = Signal(list)
    error_occurred = Signal(str)
    
    def __init__(self):
        super().__init__()
        self._active = True
        self.queue = queue.Queue()
        self.current_request = None


    def process_queue(self):
        """Обрабатывает очередь запросов"""
        while self._active:
            try:
                if not self.queue.empty():
                    expression, is_float = self.queue.get_nowait()
                    self.process_calculation(expression, is_float)
                time.sleep(0.05)
            except Exception as e:
                self.error_occurred.emit(str(e))


    def process_calculation(self, expression, is_float):
        """Выполняет один запрос"""
        try:
            params = {"float": str(is_float).lower()}
            response = requests.post(
                "http://127.0.0.1:8080/calc",
                json={"expression": expression},
                params=params,
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json().get("result")
                self.calculation_finished.emit(True, str(result), "")
                self.update_history()
            else:
                error = response.json().get("detail", "Неизвестная ошибка")
                print("ERROR CALC", error)
                self.calculation_finished.emit(False, f"Ошибка: {error}", f"HTTP {response.status_code}")
        except Exception as e:
            self.calculation_finished.emit(False, "Ошибка: сервер недоступен", str(e))


    def update_history(self):
        try:
            response = requests.get("http://127.0.0.1:8080/history", timeout=5)
            if response.status_code == 200:
                self.history_updated.emit(response.json())
        except Exception as e:
            self.error_occurred.emit(f"Ошибка истории: {str(e)}")


class DateTimeTableWidgetItem(QTableWidgetItem):
    def __init__(self, timestamp):
        super().__init__()
        self.timestamp = timestamp
        self.setText(self.format_time(timestamp))
        
        
    def format_time(self, timestamp):
        date_time = QDateTime.fromSecsSinceEpoch(timestamp)
        return date_time.toString("yyyy-MM-dd HH:mm:ss")
    
    
    def __lt__(self, other):
        return self.timestamp < other.timestamp
    
    
class SocketWorker(QObject):
    data_received = Signal(bytes)
    status_changed = Signal(bool, str)  # connected, status_text
    request_history_load = Signal()

    def __init__(self, host=HOST, port=int(PORT)):
        super().__init__()
        self._active = True
        self.host = host
        self.port = port
        self.socket = None
        self.connection_attempts = 0
        self.reconnect_interval = 5000 #через сколько миллисекунд пытаться переподключиться
        self.current_time = 0


    def create_socket(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(1)
            self.socket.connect((self.host, self.port))
            self.status_changed.emit(True, "Подключено к серверу")
            self.connection_attempts = 0
            return True
        except Exception as e:
            self.status_changed.emit(False, f"Ошибка подключения: {str(e)}")
            return False


    def listen(self):
        while self._active:
            try:
                if self.socket is None and self.create_socket():
                    continue
                
                data = self.socket.recv(1024)
                if data:
                    self.data_received.emit(data)
                else:
                    raise ConnectionError("Соединение закрыто сервером")
                    
            except socket.timeout:
                continue
            except Exception as e:
                print('error')
                self.handle_error(e)
                # self.reconnect()
                self.try_reconnect()


    def handle_error(self, error):
        print("handle_error socket: ", error)
        self.status_changed.emit(False, f"Ошибка: {str(error)}")
        if self.socket:
            self.socket.close()
        self.socket = None


    def try_reconnect(self):
        """Пытается переподключиться с фиксированным интервалом"""
        while self._active and not self.create_socket():
            self.current_time = 0
            self.connection_attempts += 1
            self.status_changed.emit(
                False, 
                f"Попытка переподключения #{self.connection_attempts} (через 5 секунд)"
            )
            while self._active and self.current_time < self.reconnect_interval:
                time.sleep(0.050)
                self.current_time = self.current_time + 50
        
        self.request_history_load.emit()
        return self.socket is not None


    def reconnect(self):
        while self.current_time < self.reconnect_interval:
            time.sleep(0.050)
            self.current_time = self.current_time + 50
        self.connection_attempts = self.connection_attempts + 1
        self.status_changed.emit(False, f"Попытка переподключения #{self.connection_attempts}")
        # time.sleep(5)


    def stop(self):
        self._active = False
        if self.socket:
            self.socket.close()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.is_float = False

        # Устанавливаем заголовок окна
        self.setWindowTitle("Калькулятор")
        icon = QIcon("images/calc.png")
        self.setWindowIcon(icon)

        # Создаем шрифт
        font = QFont()
        font.setPointSize(12)  # Размер шрифта

        # Виджеты ввода
        self.lndt_expr = QLineEdit(self)
        self.lndt_expr.setFont(font)
        self.lbl_expr = QLabel("Введите выражение:", self)
        # self.lbl_expr.setFont(font)

        # Устанавливаем валидатор для разрешенных символов
        regex = QRegularExpression(r"^[0-9(][0-9()*+/-]*$")
        self.lndt_expr.setValidator(QRegularExpressionValidator(regex, self.lndt_expr))

        # Создаем кнопку "Вычислить"
        self.pb_calculate = QPushButton("Вычислить", self)
        # self.pb_calculate.setFont(font)
        self.pb_calculate.setEnabled(False)  # Изначально кнопка выключена

        # Создаем QLineEdit "Вывод результата"
        self.lbl_result = QLabel("Нет результов", self)
        self.lbl_result.setFont(font)
        self.lbl_result.setAlignment(Qt.AlignCenter)
        self.lbl_result.setStyleSheet("color: gray")

        # Создаем QCheckBox "float"
        self.ckbx_float = QCheckBox("Режим дробного вычисления", self)

        # Создаем кнопку "Очистить"
        self.pb_clear = QPushButton("Очистить", self)
        # self.pb_clear.setFont(font)

        control_layout = QHBoxLayout()
        control_layout.addWidget(self.ckbx_float)
        control_layout.addWidget(self.pb_calculate)
        control_layout.addWidget(self.pb_clear)

        self.history_table = QTableWidget()
        self.history_table.setColumnCount(3)
        self.history_table.setHorizontalHeaderLabels(["Время вычисления", "Выражение", "Полученный ответ"])
        self.history_table.setSortingEnabled(True)
        self.history_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Настройки растяжения заголовков
        self.history_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.history_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.history_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        
        # Вертикальное растяжение таблицы
        self.history_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.history_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Модифицируем layout
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)  # Добавляем отступы
        layout.setSpacing(10)
        
        # Верхняя часть с элементами управления
        top_layout = QVBoxLayout()
        top_layout.addWidget(self.lbl_expr)
        top_layout.addWidget(self.lndt_expr)
        top_layout.addLayout(control_layout)
        top_layout.addWidget(self.lbl_result)
        
        # Добавляем все элементы в основной layout
        layout.addLayout(top_layout)
        layout.addWidget(self.history_table)  # Таблица займет все оставшееся пространство

        # Убираем addStretch() - он больше не нужен
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Статус бар
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.setup_status_bar()

        # Инициализация потока статуса сервера
        self.setup_server_status_thread()

        # Инициализация потока для вычислений
        self.setup_calculation_thread()

        # Инициализация потока для сокета
        self.setup_socket_thread()

        # Сигналы
        self.lndt_expr.textChanged.connect(self.validate_expression)
        self.pb_calculate.clicked.connect(self.send_calculation_request)
        self.pb_clear.clicked.connect(self.clear_input)
        self.ckbx_float.stateChanged.connect(self.float_checked)

        # Первоначальная загрузка
        QTimer.singleShot(100, self.load_initial_history)

        self.adjustSize()  # Автоподгонка под содержимое
        
        # self.setMinimumSize(600, 600)
        self.setGeometry(0, 0, 500, 400)


    def setup_socket_thread(self):
        self.socket_thread = QThread()
        self.socket_worker = SocketWorker()
        self.socket_worker.moveToThread(self.socket_thread)
        
        self.socket_thread.started.connect(self.socket_worker.listen)
        self.socket_worker.data_received.connect(self.handle_socket_data)
        self.socket_worker.status_changed.connect(self.handle_socket_status)
        self.socket_worker.request_history_load.connect(self.load_initial_history)
        
        self.socket_thread.start()


    def handle_socket_data(self, data):
        try:
            message = data.decode('utf-8')
            data_json = json.loads(message)
            self.status_bar.showMessage(f"Получено сообщение: {message}", 5000)
            # Здесь можно добавить обработку полученных данных
            # self.insert_history_table([data_json])
        except UnicodeDecodeError:
            self.status_bar.showMessage("Получены бинарные данные", 3000)


    def handle_socket_status(self, connected, status_text):
        color = "#28a745" if connected else "#dc3545"
        self.status_bar.showMessage(status_text, 10000)


    def setup_status_bar(self):
        # Очищаем статусбар от всех виджетов
        for child in self.status_bar.findChildren(QWidget):
            self.status_bar.removeWidget(child)
        
        # Создаем контейнер для элементов статуса
        status_container = QWidget()
        status_container.setObjectName("statusContainer")
        
        # Настраиваем горизонтальный layout
        status_layout = QHBoxLayout(status_container)
        status_layout.setContentsMargins(0, 0, 0, 0)  # Убираем все отступы
        status_layout.setSpacing(5)  # Расстояние между элементами
        
        # Индикатор статуса
        self.status_indicator = StatusIndicator()
        self.status_indicator.setFixedSize(16, 16)
        
        # Метка для кода статуса
        self.status_code_label = QLabel("")
        self.status_code_label.setFixedWidth(30)
        self.status_code_label.setAlignment(Qt.AlignCenter)
        
        # Метка для текста статуса
        self.status_text_label = QLabel("Проверка статуса...")
        
        # Добавляем элементы
        status_layout.addWidget(self.status_indicator)
        status_layout.addWidget(self.status_code_label)
        status_layout.addWidget(self.status_text_label)
        
        status_layout.setAlignment(Qt.AlignLeft)

        # Стилизация
        status_style = """
            QStatusBar {
                padding: 0;
                margin: 0;
                border: none;
            }
            #statusContainer {
                background: transparent;
                padding: 0;
                margin: 0;
            }
            QLabel {
                padding: 0;
                margin: 0;
            }
        """
        status_container.setStyleSheet(status_style)
        
        # Добавляем контейнер в статусбар
        self.status_bar.addWidget(status_container)


    def setup_server_status_thread(self):
        self.status_thread = QThread()
        self.status_worker = ServerStatusWorker()
        self.status_worker.moveToThread(self.status_thread)
        
        self.status_thread.started.connect(self.status_worker.run)
        self.status_worker.status_updated.connect(self.handle_status_update)
        self.status_thread.finished.connect(self.status_worker.deleteLater)
        
        self.status_thread.start()


    def handle_status_update(self, code, text, error):
        if code == 200:
            self.set_server_online(str(code), text)
        else:
            self.set_server_offline(str(code), text)


    def set_server_online(self, code, text):
        self.status_indicator.set_color(QColor(40, 200, 40))
        self.status_indicator.start_animation()
        self.status_code_label.setText(code)
        self.status_text_label.setText(text)
        self.status_code_label.setStyleSheet("color: #28a745; font-weight: bold;")
        self.status_text_label.setStyleSheet("color: #28a745;")


    def set_server_offline(self, code, text):
        self.status_indicator.set_color(QColor(220, 53, 69))
        self.status_indicator.stop_animation()
        self.status_code_label.setText(code)
        self.status_text_label.setText(text)
        self.status_code_label.setStyleSheet("color: #dc3545; font-weight: bold;")
        self.status_text_label.setStyleSheet("color: #dc3545;")


    def setup_calculation_thread(self):
        self.calculation_thread = QThread()
        self.calculation_worker = CalculationWorker()
        self.calculation_worker.moveToThread(self.calculation_thread)
        
        # Сигналы
        self.calculation_thread.started.connect(self.calculation_worker.process_queue)
        self.calculation_worker.calculation_finished.connect(self.handle_calculation_result)
        self.calculation_worker.history_updated.connect(self.update_history_table)
        self.calculation_worker.error_occurred.connect(self.show_error)
        
        self.calculation_thread.start()


    def send_calculation_request(self):
        expression = self.lndt_expr.text()
        if not expression:
            return
            
        # Блокируем кнопку до завершения
        self.pb_calculate.setEnabled(False)
        self.lbl_result.setText("Вычисление...")
        self.lbl_result.setStyleSheet("color: gray")
        
        # Добавляем запрос в очередь
        self.calculation_worker.queue.put((expression, self.is_float))


    def handle_calculation_result(self, success, result, error):
        """Обрабатывает результат вычисления"""
        self.pb_calculate.setEnabled(True)
        
        if success:
            self.lbl_result.setText(result)
            self.lbl_result.setStyleSheet("color: green")
        else:
            self.lbl_result.setText(result)
            self.lbl_result.setStyleSheet("color: red")
            print(f"Ошибка вычисления: {error}")


    def load_initial_history(self):
        """Загружает начальную историю через worker"""
        if hasattr(self, 'calculation_worker'):
            self.calculation_worker.update_history()


    def insert_history_table(self, history_data=None):
        """Вставляет полученные данные из сокета в таблицу"""
        if history_data is None:
            return
                
        # Отключаем сортировку во время обновления
        self.history_table.setSortingEnabled(False)
        
        try:
            # Определяем текущее количество строк
            current_row_count = self.history_table.rowCount()
            
            # Добавляем необходимое количество строк
            self.history_table.setRowCount(current_row_count + len(history_data))
            
            # Вставляем новые записи в начало таблицы
            for row_offset, entry in enumerate(history_data):
                row = current_row_count + row_offset
                timestamp = entry.get('timestamp', 0)
                expr = entry.get('expression', '')
                result = entry.get('result', '')

                time_item = DateTimeTableWidgetItem(timestamp)
                expr_item = QTableWidgetItem(expr)
                result_item = QTableWidgetItem(str(result))
                
                time_item.setTextAlignment(Qt.AlignCenter)
                expr_item.setTextAlignment(Qt.AlignCenter)
                result_item.setTextAlignment(Qt.AlignCenter)
                
                self.history_table.setItem(row, 0, time_item)
                self.history_table.setItem(row, 1, expr_item)
                self.history_table.setItem(row, 2, result_item)
                
                # Альтернативный вариант вставки в начало:
                # self.history_table.insertRow(0)
                # self.history_table.setItem(0, 0, time_item)
                # и т.д.
                
        finally:
            # Включаем сортировку обратно и сортируем
            self.history_table.setSortingEnabled(True)
            self.history_table.sortItems(0, Qt.DescendingOrder)
        
        
    def update_history_table(self, history_data=None):
        """Полностью обновляет таблицу истории из полученных данных"""
        if history_data is None:
            return
        
        # Отключаем сортировку во время обновления
        self.history_table.setSortingEnabled(False)
        
        try:
            self.history_table.setRowCount(len(history_data))
            
            for row, entry in enumerate(history_data):
                timestamp = entry.get('timestamp', 0)
                expr = entry.get('expression', '')
                result = entry.get('result', '')

                time_item = DateTimeTableWidgetItem(timestamp)
                expr_item = QTableWidgetItem(expr)
                result_item = QTableWidgetItem(str(result))
                
                time_item.setTextAlignment(Qt.AlignCenter)
                expr_item.setTextAlignment(Qt.AlignCenter)
                result_item.setTextAlignment(Qt.AlignCenter)
                
                self.history_table.setItem(row, 0, time_item)
                self.history_table.setItem(row, 1, expr_item)
                self.history_table.setItem(row, 2, result_item)
            
            self.history_table.sortItems(0, Qt.DescendingOrder)
            
        finally:
            # Включаем сортировку обратно и сортируем
            self.history_table.setSortingEnabled(True)
            self.history_table.sortItems(0, Qt.DescendingOrder)

    def float_checked(self):
        self.is_float = self.ckbx_float.isChecked()


    def clear_input(self):
        """Очищает поле ввода выражения."""
        self.lndt_expr.clear()
        self.lndt_expr.setStyleSheet("")  # Убираем красную обводку


    def validate_expression(self, text):
        """Проверяет выражение на корректность и обновляет состояние кнопки "Вычислить"."""
        result = self.validate_input(text)

        if result == 1:
            # Выражение корректно
            self.lndt_expr.setStyleSheet("")  # Убираем красную обводку
            self.pb_calculate.setEnabled(bool(text.strip()))  # Включаем кнопку, если поле не пустое
        else:
            # Выражение некорректно
            self.lndt_expr.setStyleSheet("border: 1px solid red;")  # Обводим поле красным
            self.pb_calculate.setEnabled(False)  # Блокируем кнопку


    def validate_input(self, input_str):
        """Проверяет выражение на корректность."""
        length = len(input_str)
        last_was_operator = True
        balance = 0

        i = 0
        while i < length:
            c = input_str[i]
            if c.isspace():
                i += 1
                continue
            elif c.isdigit():
                if not last_was_operator:
                    return 2

                while i < length and input_str[i].isdigit():
                    i += 1
                i -= 1
                last_was_operator = False
            elif c in {'+', '-', '*', '/'}:
                if last_was_operator:
                    return 2
                last_was_operator = True
            elif c == '(':
                if not last_was_operator:
                    return 2
                balance += 1
                last_was_operator = True
            elif c == ')':
                if last_was_operator or balance == 0:
                    return 2
                balance -= 1
                last_was_operator = False
            else:
                return 2
            i += 1

        if last_was_operator or balance != 0:
            return 2

        return 1
    
    
    def show_error(self, error_message):
        """Отображает сообщение об ошибке в статусбаре"""
        # self.status_bar.showMessage(f"Ошибка: {error_message}", 5000)
        print(f"Ошибка: {error_message}")


    def closeEvent(self, event):
        """Обработчик закрытия окна"""

        # Останавливаем оба потока
        if hasattr(self, 'status_worker'):
            self.status_worker.stop()
        if hasattr(self, 'status_thread'):
            self.status_thread.quit()
            self.status_thread.wait()
        
        if hasattr(self, 'calculation_worker'):
            self.calculation_worker._active = False
        if hasattr(self, 'calculation_thread'):
            self.calculation_thread.quit()
            self.calculation_thread.wait()
            
        if hasattr(self, 'socket_worker'):
            self.socket_worker.stop()
        if hasattr(self, 'socket_thread'):
            self.socket_thread.quit()
            self.socket_thread.wait()
        
        super().closeEvent(event)


    def showEvent(self, event):
        """Переопределение события показа для центрирования"""
        super().showEvent(event)
        self.center_window()


    def center_window(self):
        """Центрирует окно на активном экране"""
        # Получаем геометрию текущего экрана
        screen_geometry = self.screen().availableGeometry()
        
        # Рассчитываем центр экрана
        center_point = screen_geometry.center()
        
        # Устанавливаем позицию окна
        self.move(
            center_point.x() - self.width() // 2,
            center_point.y() - self.height() // 2
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
