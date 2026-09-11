# Performance Review System

## Описание решения

**Performance Review** — это веб-приложение для управления развитием сотрудников и проведения встреч 1:1 в IT-компаниях. Система автоматизирует процесс планирования обучения, отслеживания прогресса по навыкам и фиксации результатов регулярных встреч между руководителями и сотрудниками.

### Какую проблему решает

- **Отсутствие структуры** в процессе развития сотрудников
- **Ручное управление** планами обучения и встречами
- **Непрозрачность прогресса** — сложно отслеживать, кто отстаёт
- **Разрозненные данные** — информация о встречах и навыках хранится в разных местах

---

## Используемые технологии

### Frontend
- **React 18** + **TypeScript** — типизированный UI
- **Ant Design** — компонентная библиотека
- **React Router** — навигация между страницами
- **React Query (TanStack Query)** — управление серверным состоянием
- **Recharts** — визуализация аналитики
- **@uiw/react-md-editor** — Markdown-редактор для протоколов встреч

### Backend
- **FastAPI** (Python) — REST API
- **Pydantic** — валидация данных
- **PostgreSQL** — база данных

### DevOps
- **Vite** — сборка frontend
- **Docker** — контейнеризация
- **GitHub Actions** — CI/CD
- **Nginx** - прокси-сервер

---

## Описание пользовательского сценария

### Основной сценарий: "Планирование и отслеживание развития сотрудника"

**Шаг 1: Создание справочника навыков**
```
Админ → Навыки → Справочник навыков → Добавить навык
→ Указать название и направление (BACK/FRONT/QA/DEVOPS)
```

**Шаг 2: Планирование обучения**
```
Руководитель → Навыки → Годовой план обучения → Добавить навык в план
→ Выбрать навык из справочника → Указать плановую дату
```

**Шаг 3: Проведение встречи 1:1**
```
Руководитель → Встречи → Новая встреча → Выбрать сотрудника
→ Заполнить markdown-протокол → Отметить статусы навыков
(Зачтён / В процессе / Проблема) → Прикрепить файлы/ссылки
```

**Шаг 4: Отслеживание прогресса**
```
Сотрудник/Руководитель → Навыки → Годовой план
→ Видит статусы: Запланирован → В процессе → Зачтён
→ Анализирует комментарии к проблемам
```

**Шаг 5: Аналитика**
```
Руководитель → Аналитика → Выбрать подразделение/сотрудника
→ Просмотр графика прогресса → Выявление отстающих
```

---

## Функциональность MVP

### Реализовано

| Модуль | Функции |
|--------|---------|
| **Сотрудники** | Таблица с фильтрацией по направлениям и подразделениям |
| **Справочник навыков** | CRUD операции (создание, редактирование, удаление) |
| **Годовой план** | Добавление навыков с плановыми датами, статусы обучения |
| **Встречи 1:1** | Протоколы с Markdown, отметки по навыкам, вложения |
| **Аналитика** | Графики прогресса по подразделению и сотруднику |
| **Структура** | Дерево подразделений с иерархией |

## Дополнительный функционал

### Реализовано сверх требований:

- **Мониторинг**

---

## Установка и запуск

### Требования
- Node.js 18+
- Python 3.10+
- PostgreSQL 14+

### Frontend
```bash
cd frontend
npm install
npm run dev
```
Приложение доступно на `http://localhost:5173`

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```
API доступно на `http://localhost:8000`

### Docker (рекомендуется)
```bash
docker-compose up --build
```

---

## 📁 Структура проекта

```
hackathon_reactionstack/
│
├── frontend/                          # Frontend приложение (React + TypeScript)
│   ├── node_modules/                  # Зависимости npm
│   ├── public/                        # Статические файлы
│   ├── src/
│   │   ├── api/                       # API-клиенты и типы
│   │   │   ├── analytics.ts           # API для аналитики
│   │   │   ├── auth.ts                # API для аутентификации
│   │   │   ├── client.ts              # HTTP-клиент (axios)
│   │   │   ├── departments.ts         # API для подразделений
│   │   │   ├── meetings.ts            # API для встреч
│   │   │   ├── permissions.ts         # API для прав доступа
│   │   │   ├── skills.ts              # API для навыков
│   │   │   ├── types.ts               # TypeScript типы и интерфейсы
│   │   │   └── users.ts               # API для пользователей
│   │   │
│   │   ├── assets/                    # Статические ресурсы
│   │   │   ├── hero.png
│   │   │   ├── react.svg
│   │   │   └── vite.svg
│   │   │
│   │   ├── components/                # Переиспользуемые компоненты
│   │   │   ├── employee/
│   │   │   │   └── EmployeeCardModal.tsx
│   │   │   ├── layout/
│   │   │   │   └── AppLayout.tsx
│   │   │   ├── skill/
│   │   │   │   ├── SkillProgressBar.tsx
│   │   │   │   └── SkillStatusBadge.tsx
│   │   │   └── ui/
│   │   │       └── SkillBadge.tsx
│   │   │
│   │   ├── pages/                     # Страницы приложения
│   │   │   ├── AnalyticsPage.tsx
│   │   │   ├── EmployeesPage.tsx
│   │   │   ├── LoginPage.tsx
│   │   │   ├── MeetingsPage.tsx
│   │   │   ├── OrgTreePage.tsx
│   │   │   └── SkillsPage.tsx
│   │   │
│   │   ├── utils/                     # Вспомогательные функции
│   │   │   └── buildTree.ts
│   │   │
│   │   ├── App.css
│   │   ├── App.tsx                    # Корневой компонент с роутингом
│   │   ├── index.css
│   │   └── main.tsx                   # Точка входа
│   │
│   ├── .gitignore
│   ├── eslint.config.js
│   ├── index.html
│   ├── package.json
│   ├── package-lock.json
│   ├── tsconfig.app.json
│   ├── tsconfig.json
│   ├── tsconfig.node.json
│   └── vite.config.ts
│
├── backend/                           # Backend приложение (FastAPI + Python)
│   ├── alembic/                       # Миграции базы данных
│   │   ├── versions/                  # Файлы миграций
│   │   ├── env.py
│   │   └── script.py.mako
│   │
│   ├── app/                           # Основное приложение
│   │   ├── api/                       # API эндпоинты
│   │   │   └── v1/                    # Версия API v1
│   │   │       ├── analytics.py
│   │   │       ├── auth.py
│   │   │       ├── departments.py
│   │   │       ├── meetings.py
│   │   │       ├── permissions.py
│   │   │       ├── skills.py
│   │   │       └── users.py
│   │   │
│   │   ├── core/                      # Ядро приложения
│   │   │   ├── config.py              # Конфигурация
│   │   │   ├── database.py            # Подключение к БД
│   │   │   └── security.py            # Безопасность (JWT)
│   │   │
│   │   ├── models/                    # ORM модели (SQLAlchemy)
│   │   │   ├── department.py
│   │   │   ├── meeting.py
│   │   │   ├── skill.py
│   │   │   └── user.py
│   │   │
│   │   ├── schemas/                   # Pydantic схемы
│   │   │   ├── analytics.py
│   │   │   ├── department.py
│   │   │   ├── meeting.py
│   │   │   ├── permissions.py
│   │   │   ├── skill.py
│   │   │   └── user.py
│   │   │
│   │   ├── services/                  # Бизнес-логика
│   │   │   ├── analytics_services.py
│   │   │   ├── notifier.py
│   │   │   └── tree_services.py
│   │   │
│   │   ├── deps.py                    # Зависимости FastAPI (DI)
│   │   ── main.py                    # Точка входа
│   │
│   ├── .gitignore
│   ├── alembic.ini
│   ├── requirements.txt
│   └── README.md
│
├── .gitignore                         # Глобальный .gitignore
├── docker-compose.yml                 # Docker Compose для запуска всего проекта
── README.md                          # Основная документация проекта
└── docs/                              # Дополнительная документация
    └── api.md                         # Документация API
```

---

##  Демонстрация

### Развёрнутое приложение
🔗 **URL:** https://reactionstack.135.106.217.211.sslip.io/

### Тестовые учётные данные
- **Admin:** admin / pass123
- **User:** junior / pass123
- **Lead:** lead / pass123

### Мониторинг
**URL** https://grafana.reactionstack.135.106.217.211.sslip.io
**Login** admin
**Pass** 442ba46dc3e32499554ad6c6

---

## 👥 Команда

- **Frontend Developer:** Арсений и Владислав — React, TypeScript, UI/UX
- **Backend Developer:** Вадим и Иван — FastAPI, PostgreSQL
- **DevOps** Максим — Python, Bash, Grafana, Docker, GitHub Actions, PostgreSQL, nginx

---

## 🤖 Использование AI-инструментов

В проекте использовались следующие AI-инструменты:

| Этап | Инструмент | Задача |
|------|-----------|--------|
| Генерация идей | Claude | Проектирование архитектуры и UX |
| Frontend | Qwen Chat | Генерация компонентов React |
| Backend| Gemini | Написание кода |