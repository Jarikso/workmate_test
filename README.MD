# Django Log Analyzer

Анализатор логов Django-приложения, который предоставляет статистику по обработчикам (handlers) и уровням логирования.

## Структура проекта
![Снимок экрана 2025-04-15 в 14.01.27.png](image/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202025-04-15%20%D0%B2%2014.01.27.png)
## Функциональность
- Анализирует логи Django-приложения
- Группирует данные по обработчикам (endpoints)
- Подсчитывает количество запросов по уровням логирования:
  - DEBUG
  - INFO
  - WARNING
  - ERROR
  - CRITICAL
- Генерирует отчет в виде таблицы


### Приложение запускается по команде
python3 main.py logs/app1.log logs/app2.log logs/app3.log --report handlers

### Аргументы командной строки<br/>
log_files: Список файлов логов для анализа (обязательный)<br/>
--report: Тип отчета (по умолчанию: handlers)<br/>
--report handlers # Отчет по обработчикам (единственный доступный вариант)<br/>
### Тестирование
#### Для запуска тестов:<br/>
pytest test.py -v<br/>
#### Тесты проверяют:<br/>
Парсинг строк логов (успешные запросы, ошибки)<br/>
Обработку отсутствующих файлов<br/>
Основную логику анализа логов<br/>

## Пример вывода
![Снимок экрана 2025-04-15 в 14.01.48.png](image/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202025-04-15%20%D0%B2%2014.01.48.png)

## Расширяемость
При запуске приложения можно добавить команты формата "--report system", "--report all" или "--report level".
Эти команды можно использовать для отображения системных логов, всех логов. Последний может предоставлять отчет о всех лога в проекте.
Для реализации необходимо внети изменения в код, в частности

parser.add_argument('--report', 
                   choices=['handlers', 'system', 'all', 'level'], 
                   default='handlers',
                   help='Тип отчета')
Реализуйте соответствующую логику в функции parse_logs()

### Примечание
К сожалению за тестовое задание сел крайне поздно, поэтому не смог в коде показать его расширяемость.