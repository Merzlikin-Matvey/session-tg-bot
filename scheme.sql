create table exams
(
    id           serial
        primary key,
    name         varchar,
    timestamp    timestamp,
    tasks_paths  text,
    participants character varying[],
    started      boolean,
    examiners    text[],
    user_tasks   json
);

create table users
(
    telegram_id        varchar default -1 not null
        primary key,
    full_name          varchar,
    is_admin           boolean,
    registered_exam_id integer
);