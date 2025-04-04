# КОМАНДА "МУГИВАРЫ"

### О проекте - Release-v1

Этот проект представляет собой связку `интерфейс-сервер-калькулятор`.

<details>
<summary>Описание интерфейса</summary>

Интерфейс содержит: 
- Текстовое поле для ввода выражения
- Переключение режима дробного вычисления
- Кнопку "Вычислить"
- Кнопку "Очистить" выражение
- Текст, отображающий ответ от сервера с результатом работы калькулятора или ошибки
- Таблицу с историей вычислений с сервера
- Строка описывающая состояние сервера и подключение к нему

</details>

<details>
<summary>Описание сервера</summary>

- Является асинхронным и поддерживает одновременное подключение множества клиентов с помощью сокетов и отдельных потоков для каждого клиента.
- Каждое успешное вычисление записывается в историю, реализованную в виде базы данных и хранящуюся в репозитории.
- При получении успешного результата вычислений клиенту, запросившему вычисление, передаётся, помимо результата, история всех вычислений для синхронизации.
- При получении успешного результата вычислений всем клиентам высылается разница(`dif`) между имеющейся у клиентов историей вычислений и хранящейся на сервере.
- При возникновении ошибки при вычислении, ошибка не заносится в историю, соответственно ошибку видит только клиент, запросивший вычисление.
- Сокет клиента удаляется из оперативной памяти сервера в том случае, если при попытке выслать `dif` клиент не отвечает (Клиент был закрыт или соединение было разорвано).

</details>

<details>
<summary>Описание калькулятора</summary>

- Ввод данных осуществляется через стандартный ввод данных (stdin).
- Вывод осуществляется через стандартный вывод данных (stdout).
- Объем входных данных составляет менее 1 Кбайт (иначе UB).
- Окончание ввода определяется после считывания EOF.
- Разрешена только кодировка [0-9()*+\/\s-] (в противном случае возвращаемый код программы не равен 0).
- 0-9 соответствует одному символу в диапазоне от 0 (индекс 48) до 9 (индекс 57) (с учетом регистра).
- ()\*+ соответствует одному символу в списке ()\*+ (с учетом регистра).
- \/ соответствует символу / с индексом (или) буквально (с учетом регистра) \s соответствует любому символу пробела (эквивалентно [ \r\n\t\f\v ]).
- \- соответствует символу - с индексом (или) буквально (с учетом регистра).
- Допустимы только правильные арифметические выражения (в противном случае возвращаемый код не равен 0).
- Все числа в данном выражении являются целыми числами из диапазона $[0 \dots 2 \times 10^9]$ (в противном случае UB).
- Все промежуточные результаты (для любого допустимого порядка вычисления) укладываются в диапазон $[-2 \times 10^9 \dots +2 \times 10^9]$ (иначе UB).
- Должен поддерживаться флаг --float, который переводит вычисления приложения в режим вещественных чисел, точность которых до 4 знаков после запятой $(10^{-4}).$

</details>

### Сборка и запуск программы

Управление проектом и его файлами происходит с помощью Makefile. Требования к запуску: установленный `docker`, `docker-compose`. Пользователь(username) должен состоять в группе `docker`:

```bash
gpasswd -a username docker
```

1. Чтобы собрать и запустить сервер с базой данных с помощью `docker-compose`:

```bash
make run-compose
```

2. Чтобы запустить интерфейс:

```bash
make run-gui
```

Данных команд более чем достаточно для работы с проектом при соблюдении требований. Ниже описано еще несколько команд для работы с `docker`.

Чтобы **отдельно** собрать и запустить сервер и базу данных с помощью `docker`:

```bash
make run-server-docker
make run-db-docker
```

Для **остановки** сервера и базы данных соответственно с помощью `docker`:

```bash
make stop-server-docker
make stop-db-docker
```

Для **очистки** контейнеров и образов с помощью `docker`:

```bash
make clean-all-containers
make clean-all-images
```

С другими возможными командами можно ознакомиться непосредственно в `Makefile`

### Дополнительная информация

**Команда состоит из:**

![В главных ролях](./drive.png)

- [Самый ответственный и скромный в мире тимлид](https://github.com/Pancko)
- [Уставший GUI-щик](https://github.com/Azriel230)
- [Гений универсал](https://github.com/Guolinang)
- [Злой DevOps-ер](https://github.com/Ne-ko-Chan)

<details>
<summary>Древние свитки (Подробные шаги развития проекта)</summary>

## MVP - Калькулятор

### О проекте

Этот проект представляет собой консольное приложение — Калькулятор.
Требования к программе:

- Ввод данных осуществляется через стандартный ввод данных (stdin).
- Вывод осуществляется через стандартный вывод данных (stdout).
- Объем входных данных составляет менее 1 Кбайт (иначе UB).
- Окончание ввода определяется после считывания EOF.
- Разрешена только кодировка [0-9()*+\/\s-] (в противном случае возвращаемый код программы не равен 0).
- 0-9 соответствует одному символу в диапазоне от 0 (индекс 48) до 9 (индекс 57) (с учетом регистра).
- ()\*+ соответствует одному символу в списке ()\*+ (с учетом регистра).
- \/ соответствует символу / с индексом (или) буквально (с учетом регистра) \s соответствует любому символу пробела (эквивалентно [ \r\n\t\f\v ]).
- \- соответствует символу - с индексом (или) буквально (с учетом регистра).
- Допустимы только правильные арифметические выражения (в противном случае возвращаемый код не равен 0).
- Все числа в данном выражении являются целыми числами из диапазона $[0 \dots 2 \times 10^9]$ (в противном случае UB).
- Все промежуточные результаты (для любого допустимого порядка вычисления) укладываются в диапазон $[-2 \times 10^9 \dots +2 \times 10^9]$ (иначе UB).
- Должен поддерживаться флаг --float, который переводит вычисления приложения в режим вещественных чисел, точность которых до 4 знаков после запятой $(10^{-4}).$

### Сборка и запуск программы

Чтобы собрать программу, вам нужен компилятор `gcc` или `clang`. Следуйте этим шагам:

1. Откройте терминал в папке с проектом.
2. Напишите и запустите команду:

```bash
make all
```

Чтобы запустить программу в режиме целых чисел, введите в терминал команду:

```bash
make run-int
```

Чтобы запустить программу в режиме вещественных чисел, введите в терминал команду:

```bash
make run-float
```

### Как это работает?

Для переключения режимов используется глобальный флаг flag_float. 0 — целые числа, 1 — вещественные числа.
Для разделения типов long (целые) и double (дробные) используется объединение Number.
Для вычислений используется структура Stack. В ней содержится массив данных data с достаточно большим размером STACK_SIZE, и переменная top, указывающая на вершину стека.
Для работы со стеком были написаны следующие функции:

- initializeStack — инициализирует стек.
- isEmptyStack и isFullStack — проверяют стек на пустоту и заполненность.
- pushStack — кладет элемент в стек.
- popStack — вытаскивает верхний элемент стека и возвращает его.
- peekStack — возвращает верхний элемент стека, но не удаляет его.
Для проверки корректности требований к программе Калькулятор были написаны функции:
- checkNumberSize — проверяет, что число находится в диапазоне $[-2 \times 10^9 \dots +2 \times 10^9]$.
- validateInput — парсер входного выражения, проверяющий его корректность.
Для вычисления выражения были написаны функции:
- priorityOperations — возвращает номер операции (ее приоритет).
- applyOperation — на вход получает два числа и код операции, а возвращает результат вычисления (исключая деление на 0)
- calculatingExpression — главная функция, которая вычисляет выражение. Создается два стека: для чисел и операций, далее происходит парсинг выражения: числа и операции попадают в стек. Если есть закрывающаяся скобка, то производятся вычисления выражения до тех пор, пока из стека операций не достанем открывающуюся скобку. В конце вычисляется выражение и возвращается его значение.

В функции main считываем флаг --float, выставляем значение флага flag_float, проверяется корректность выражения и производится его вычисление. В конце оно выводится в stdout.

## RC1 - Сервер

Следующий этап развития проекта - сервер, реализованный в **src/server.py** и запускаемый с помощью команды:

```bash
make run-server
```

### Функциональные особенности сервера

- Запуск в локальной сети (127.0.0.1).
- Сборка калькулятора при запуске сервера.
- Получение POST запроса с выражением для вычисления.
- Запуск калькулятора с полученным выражением.
- Построение отчётов с помощью `structlog`, выведение их в консоль и сохранение в `JSON` формате.
- Выдаёт код 500 при возникновении ошибок на любом этапе обработки и выполнения запроса.
- Выдаёт код 200 при корректной работе сервера и калькулятора.

### Use case - отправить выражение на вычисление

- Пользователь отправляет POST-запрос с выражением на сервер.
- Сервер передает выражение калькулятору.
- Калькулятор вычисляет результат или возвращает ошибку.
- Сервер возвращает результат или описание ошибки пользователю.

### Дневники разработки rc1

- 7.03.2025: `GEAR-1`, разработана и протестирована первая версия сервера, обрабатывающая POST запросы и выдающая ответ от калькулятора.
- 8.03.2025: `GEAR-2`, `GEAR-3`, доработан и протестирован функционал логирования, добавлена make-команда для сборки.

## RC2 - GUI

Ипользуем `pyside6`, да помилует нас Господь, для разработки графического интерфейса взаимодействия с сервером.
Для запуска этого чуда используем:

```bash
make run-app
```

### Описание и требования к интерфейсу

- Интерфейс содержит: текстовое поле для ввода, checkbox "float", кнопку "Вычислить", текстовое поле для результатов работы.
- Интерфейс программы выстроен с помощью Vertical Layout, где сверху вниз:
  - 1 уровень: текстовое поле для ввода и checkbox "float".
  - 2 уровень: кнопка "Вычислить".
  - 3 уровень: текстовое поле для результатов работы.
- Текстовое поля для ввода изначально пустое. Пользователь может вводить в него знаки [0-9()*+\/-]. Первым символом может быть только цифра или открывающая скобка.
- Checkbox "float" отвечает за наличие флага "--float" в POST-запросе, который отправляется на сервер.
- Кнопка "Вычислить" не активна (не доступна для нажатия) пока текстовое поле для ввода пусто. Кнопка становится активной если в текстовом поле для ввода появляются символы.
- Текстовое поле для результатов работы изначально пустое. Пользователь не может вводить информацию в данное поле. Текстовое поле для результатов работы изменяется при получении результата работы сервера. В нём пишется результат работы калькулятора или описание возникшей ошибки.

### Use cases

1. Ввод выражения:
   - Пользователь вводит выражение в текстовое поле.
   - Кнопка "Вычислить" становится активной
2. Отправить запрос на сервер:
   - Пользователь нажимает кнопку "Вычислить".
   - Программа отправляет POST-запрос на сервер.
3. Получить результат:
   - Интерфейс получает ответ от сервера и отображает результат или описание ошибки.

### UML-диаграмма данного этапа

![Alt text](/UML.png)

### Дневники разработки rc2

- 23.03.2025: `GEAR-6`, `GEAR-7`, разработан графический интерфейс и внесены поправки в makefile.
- 25.03.2025: Протестирован написанный функционал и закрыт соответствующий EPIC.

## Release-v1 - Множественное растройство личности (клиентов)

**Решаемая задача**: возможность подключения и одновременной работы с сервером множества клиентов; возможность получать информацию об истории вычислений, собранной со всех клиентов.

### Описание и требования к работе клиента и сервера

**Клиент:**

- При запросе вычислений, помимо ответа, получает историю вычислений с сервера.
- История отображается в виде таблицы, отсортированной по времени вычислений, где:
  - 1 столбец - время вычисления;
  - 2 столбец - введенное выражение;
  - 3 столбец - результат вычисления.

**Сервер:**

- Становится асинхронным и поддерживает одновременное подключение множества клиентов с помощью сокетов и отдельных потоков для каждого клиента.
- Каждое успешное вычисление записывается в историю, реализованную в виде базы данных и хранящуюся в репозитории.
- При получении успешного результата вычислений клиенту, запросившему вычисление, передаётся, помимо результата, история всех вычислений для синхронизации.
- При получении успешного результата вычислений всем клиентам высылается разница(`dif`) между имеющейся у клиентов историей вычислений и хранящейся на сервере.
- При возникновении ошибки при вычислении, ошибка не заносится в историю, соответственно ошибку видит только клиент, запросивший вычисление.
- Сокет клиента удаляется из оперативной памяти сервера в том случае, если при попытке выслать `dif` клиент не отвечает (Клиент был закрыт или соединение было разорвано).

### Дневники разработки Release-v1
- 26.03.2025: `GEAR-13`, `GEAR-14`. Перенесён калькулятор и тесты для него из другой команды (произошло слияние). Makefile переписан с учетом всех необходимых зависимостей для запуска.
- 27.03.2025: `GEAR-9`, `GEAR-10`, `GEAR-13`. Подготовка GUI к последующим изменениям, сервер переписан на FastAPI. Редактировался Makefile.
- 28.03.2025: `GEAR-10`. Сервер работает в отдельном терминале, а не в бекграунде.
- 29.03.2025: `GEAR-11`. Создание базы данных.
- 30.03.2025: `GEAR-16`. Докеризация сервера и базы данных.
- 01.04.2025: ПРОФЕССИОНАЛЬНЫЙ ПРАЗДНИК КОМАНДЫ ДУРАКОВ, НИКТО НИЧЕГО НЕ ДЕЛАЛ.
- 02.04.2025: `GEAR-15`, `GEAR-16`. GUI: написан тротлинг для обработки состояния сервера. Фиксы докера.
- 03.04.2025: `GEAR-12`, `GEAR-19`. Написана работа с асинхронными сокетами для сервера. Добавлен docker-compose, налажена первая версия CI/CD Pipeline-а.
- 04.04.2025: `GEAR-17`, `GEAR-18`, `GEAR-19`. GUI полностью адаптирован для работы с WebSocket. На сервер возвращёны structlog логи. Фиксы и дебаги docker-compose.

</details>