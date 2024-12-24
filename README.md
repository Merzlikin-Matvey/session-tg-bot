# Иновационный бот для сессий
В нашем боте реализованы все современные стандарты разработки: наличие тестов, CI/CD, postgres и многое другое.

# Что тут будет?

- [Функционал](#функционал)

- [Запуск проекта](#запуск-проекта)

- [Архитектура БД](#архитектура-бд)

- [Тестирование](#тестирование)

- [CI-CD](#ci-cd)

- [Разработчики](#разработчики)





## Функционал:

1. Добаление любого количества билетов в разных форматах (.zip, .rar, .pdf, картинки).

2. Добавление любого вида экземна с билетами, не важно что это.
   
3. Inline клавиатуры, которые облегчают user expiriencе.
   
4. Возможность попросить консультацию у учителя. (и ответить на нее со стороны учителей)
   
5. Автоматическая раздача билетов в установленное время экзамена.


## Запуск проекта

Для запуска нашего проекта вам нужно создать .env файл по образцу:
```
BOT_API_TOKEN=7643599710:AAEz1o1jcelTobwk-ZZftdGbaO_B8KgoLhU

DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=77.105.147.62
DB_PORT=5432
```
После чего прописать в консоли следующие команды:
```shell
python -m .venv .venv
. ./.venv/Scripts/acrivate
pip install -r requirements.txt
python -m src 
```
После таких махинаций проект запустится!



## Архитектура БД
В нашем проекте есть две postgres таблицы заполняемые по образцу:
- таблица экзаменов:
  ```sql
  create table exams
  (
      id           serial
          primary key,
      name         varchar,
      timestamp    timestamp,
      tasks_paths  text,
      participants character varying[],
      started      boolean,
      examiners    text[]
  );
  ```
- таблица пользователей:
  ```sql
  create table users
  (
      telegram_id        varchar default -1 not null
          primary key,
      full_name          varchar,
      is_admin           boolean,
      registered_exam_id integer
  );
  ```


## Тестирование
В нашем проекте есть тесты, которые находятся в папке ```tests```. В дальнейшем они будут использоваться в CI/CD.


## CI-CD
Пока скип
```123123```



## Разработчики:
### Матвей,Лев,Алексей
