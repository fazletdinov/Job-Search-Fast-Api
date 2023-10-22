# Проект под названием "Поиск работы"

Это Пет проект, который еще дорабатывается. 
Планирую прикрутить чат, возможность оценки вакансии, комментарии
и многое другое

Проект реализован с помощью Fastapi, SQLAlchemy, PostgreSql, alembic асинхронно

## Чтобы запустить проект у себя локально, вам необохимо
Склонировать репозиторий

`git clone https://github.com/fazletdinov/Job-Search-Fast-Api.git

Далее необходимо создать виртуальное окружение
и установить все необходимые зависимости

```
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

```
python3 main
```
Вышеуказанная команда запустит приложение
### Ручка для регистрации пользователя

`POST /auth/register`

### Пример запроса
`POST /auth/register`
```json
{
  "email": "user@example.com",
  "password": "string"
}
```
### Ответ

Успешный ответ приходит с кодом `201` и содержит тело:

```json
{
  "id": "43491e32-683d-42ab-9f48-a22da932dd72",
  "email": "user@example.com",
  "is_active": true,
  "is_superuser": false,
  "is_verified": false
}
```

### Метод yужен для получения токена
### Пример запроса
`POST /auth/jwt/login`

```json
{
  "username": "user@example.com",
  "password": "string"
}

### Ответ
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiOTIyMWZmYzktNjQwZi00MzcyLTg2ZDMtY2U2NDJjYmE1NjAzIiwiYXVkIjoiZmFzdGFwaS11c2VyczphdXRoIiwiZXhwIjoxNTcxNTA0MTkzfQ.M10bjOe45I5Ncu_uXvOmVV8QxnL-nZfcH96U90JaocI",
  "token_type": "bearer"
}
```

### CRUD операции для создания вакансий
`GET /vacansy` - Получение списка вакансий, могут получить все, в том числе неавторизованные, 
применяется фильтрация, пагинация
`GET /vacansy/{vacansy_id}` - Получение вакансии по id, так же могут получить все
`POST /vacansy` - Добавление вакансии, могут лишь авторизованные пользователи
`PATCH /vacansy/{vacansy_id}` - Обнговление вакансии, могут лишь авторизованные пользователи и лишь свою, админы могут коректировать любые
`DELETE /vacansy/{vacansy_id}` - Удаление вакансии, могут лишь авторизованные пользователи и лишь свою,
админы могут удалять любые

### Пример запроса
`GET /vacansy`
 
### Ответ
```json
{
  "items": [
    {
      "id": 2,
      "place_of_work": "Bank of Amerika",
      "required_specialt": "Bank",
      "proposed_salary": "string",
      "working_conditions": "string",
      "required_experience": "string",
      "vacant": "string",
      "created": "2023-10-21T06:47:36.865714Z"
    },
    {
      "id": 3,
      "place_of_work": "Google",
      "required_specialt": "Google",
      "proposed_salary": "string",
      "working_conditions": "string",
      "required_experience": "string",
      "vacant": "string",
      "created": "2023-10-21T06:47:54.009795Z"
    },
    {
      "id": 4,
      "place_of_work": "Microsoft",
      "required_specialt": "Microsoft",
      "proposed_salary": "string",
      "working_conditions": "string",
      "required_experience": "string",
      "vacant": "string",
      "created": "2023-10-21T06:48:16.328879Z"
    }
  ],
  "total": 3,
  "limit": 50,
  "offset": 0
}
```

### CRUD операции для создания резюме
`GET /resume` - Получение списка резюме, могут получить все, в том числе неавторизованные, 
применяется фильтрация, пагинация
`GET /resume/{resume_id}` - Получение резюме по id, так же могут получить все
`POST /resume` - Добавление резюме, могут лишь авторизованные пользователи
`PATCH /resume/{resume_id}` - Обнговление резюме, могут лишь авторизованные пользователи и лишь свою, админы могут коректировать любые
`DELETE /resume/{resume_id}` - Удаление резюме, могут лишь авторизованные пользователи и лишь свою,
админы могут удалять любые
```
### Автор
[Idel Fazletdinov - fazletdinov](https://github.com/fazletdinov)