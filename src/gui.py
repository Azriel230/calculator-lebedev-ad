import sys
import requests
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QCheckBox, QLineEdit, QVBoxLayout,QHBoxLayout, QWidget, QStatusBar
from PySide6.QtGui import QRegularExpressionValidator, QFont
from PySide6.QtCore import QRegularExpression, QTimer, Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.is_float = False

        # Устанавливаем заголовок окна
        self.setWindowTitle("Калькулятор")

        # Создаем шрифт
        font = QFont()
        font.setPointSize(12)  # Размер шрифта

        # Создаем QLineEdit "Ввод выражения"
        self.lndt_expr = QLineEdit(self)
        #self.lndt_expr.setPlaceholderText("выражение...")
        self.lndt_expr.setFont(font)

        self.lbl_expr = QLabel("Введите выражение:", self)
        self.lbl_expr.setFont(font)

        # Устанавливаем валидатор для разрешенных символов
        regex = QRegularExpression(r"^[0-9(][0-9()*+/-]*$")
        validator = QRegularExpressionValidator(regex, self.lndt_expr)
        self.lndt_expr.setValidator(validator)

        # Создаем кнопку "Вычислить"
        self.pb_calculate = QPushButton("Вычислить", self)
        self.pb_calculate.setFont(font)
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
        self.pb_clear.setFont(font)

        control_layout = QHBoxLayout()
        control_layout.addWidget(self.ckbx_float)
        control_layout.addWidget(self.pb_calculate)
        control_layout.addWidget(self.pb_clear)

        # Устанавливаем основную компоновку
        layout = QVBoxLayout()
        layout.setSpacing(10)  # Устанавливаем небольшой отступ между виджетами
        layout.addWidget(self.lbl_expr)
        layout.addWidget(self.lndt_expr)
        layout.addLayout(control_layout)
        layout.addWidget(self.lbl_result)

        # Убираем растяжение между виджетами
        layout.addStretch(0)  # Убираем лишнее пространство внизу

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Устанавливаем размеры окна
        self.setGeometry(500, 100, 100, 100)

        # Подключаем сигналы
        # Сигнал изменения текста для проверки корректности ввода
        self.lndt_expr.textChanged.connect(self.validate_expression)
        # Сигнал нажатия кнопки "Вычислить"
        self.pb_calculate.clicked.connect(self.send_calculation_request)
        # Сигнал нажатия кнопки "Очистить"
        self.pb_clear.clicked.connect(self.clear_input)
        # Сигнал изменения состояния чекбокса
        self.ckbx_float.stateChanged.connect(self.float_checked)

        # Добавляем статусбар
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.update_server_status()  # Первоначальная проверка статуса сервера

        # Таймер для регулярной проверки статуса сервера
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_server_status)
        self.status_timer.start(5000)  # Проверка каждые 5 секунд

    def update_server_status(self):
        """Проверяет статус сервера и обновляет статус бар."""
        try:
            response = requests.get("http://127.0.0.1:8080/")
            if response.status_code == 200:
                self.status_bar.showMessage("Сервер запущен", 5000)
                self.status_bar.setStyleSheet("color: green")
            else:
                self.status_bar.showMessage("Сервер не отвечает", 5000)
                self.status_bar.setStyleSheet("color: red")
        except requests.exceptions.RequestException:
            self.status_bar.showMessage("Сервер недоступен", 5000)
            self.status_bar.setStyleSheet("color: red")

    def send_calculation_request(self):
        """Отправляет POST-запрос на сервер для вычисления выражения."""
        expression = self.lndt_expr.text()
        try:
            params = {"float": str(self.is_float).lower()}
            response = requests.post(
                "http://127.0.0.1:8080/calc",
                json={"expression": expression},
                params=params
            )
            if response.status_code == 200:
                result = response.json().get("result")
                self.lbl_result.setText(str(result))
                self.lbl_result.setStyleSheet("color: green")
            else:
                error = response.json().get("error", "Неизвестная ошибка")
                self.lbl_result.setText(f"Ошибка: {error}")
                self.lbl_result.setStyleSheet("color: red")
        except requests.exceptions.RequestException:
            self.lbl_result.setText("Ошибка: сервер недоступен")
            self.lbl_result.setStyleSheet("color: red")

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


if __name__ == "__main__":
    # Создаем экземпляр приложения
    app = QApplication(sys.argv)

    # Создаем и показываем главное окно
    window = MainWindow()
    window.show()

    # Запускаем цикл обработки событий
    sys.exit(app.exec())