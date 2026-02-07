<div align="center">

<h1 style="display:flex; align-items:center; justify-content:center; gap:8px; margin-bottom: 20px">
  <img src="docs/logo.png" alt="2GIS" width="32">
  Парсер 2ГИС
</h1>

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&labelColor=090909)](https://python.org)
[![Scrapy](https://img.shields.io/badge/Scrapy-2.13-60A839?style=for-the-badge&logo=scrapy&&labelColor=090909)](https://scrapy.org)
[![License](https://img.shields.io/badge/License-Non--Commercial-E63946?style=for-the-badge&logo=googledocs&labelColor=090909)](LICENSE.md)

Автоматический сбор данных об организациях из 2ГИС по городам и рубрикам.

`Отзывы` · `Меню и прайсы` · `Фото и медиа` · `Контакты` · `Конвертация в Excel`

---

</div>

## Возможности

- Сбор **десятков тысяч** организаций за секунды
- Поддержка массового парсинга по городам и рубрикам
- Извлечение:
  - **Организации** — сбор по городам и рубрикам с пагинацией
  - **Отзывы** — сбор отзывов пользователей
  - **Меню и прайсы** — загрузка меню ресторанов и прайс-листов организаций
  - **Медиа** — сбор медиа карточек с разбивкой по альбомам
  - **Города и рубрики** — автоматическое получение справочников 2ГИС
- **Excel-конвертер** — конвертация JSON в XLSX
- **Прокси** — встроенная ротация прокси (опционально)

## Установка

```bash
# 1. Клонирование репозитория
git clone https://github.com/ruvn-1fgas/2gis-parser.git
cd 2gis-parser/app

# 2. Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# 3. Установка зависимостей
pip install -r requirements.txt
```


## Использование

### 1. Получение справочных данных

Перед парсингом организаций необходимо собрать базовые справочники:

```bash
# Список всех городов
scrapy crawl cities

# Список всех рубрик
scrapy crawl rubrics
```

Результаты сохраняются в:
- `cities_full.json`
- `rubrics_full.json`

### 2. Парсинг организаций

```bash
# По конкретным рубрикам и городам (через файлы)
scrapy crawl organizations
  -a rubrics_file=rubrics.json
  -a cities_file=cities.json

# По кодам рубрик
scrapy crawl organizations
  -a rubrics_codes=373,89,969 
  -a cities_ids=32,38

# По стране (все города указанной страны)
scrapy crawl organizations
  -a rubrics_file=rubrics.json
  -a country=ru

# Все рубрики, все города
scrapy crawl organizations
  -a parse_all_rubrics=true
  -a parse_all_cities=true
```

### 3. Дополнительные данные

```bash
# С отзывами
scrapy crawl organizations
  -a rubrics_file=rubrics.json
  -a cities_file=cities.json
  -a parse_reviews=true

# С меню/прайсами
scrapy crawl organizations
  -a rubrics_file=rubrics.json
  -a cities_file=cities.json
  -a parse_menus=true

# С фото и медиа
scrapy crawl organizations
  -a rubrics_file=rubrics.json
  -a cities_file=cities.json
  -a parse_media=true

# Всё вместе
scrapy crawl organizations
  -a rubrics_file=rubrics.json
  -a cities_file=cities.json
  -a parse_reviews=true
  -a parse_menus=true
  -a parse_media=true
```

## Структура проекта

```
2gis-parser/
├── app/
│   ├── gis/                            # Scrapy-проект
│   │   ├── spiders/
│   │   │   ├── cities_spider.py        # Паук: список городов
│   │   │   ├── rubrics_spider.py       # Паук: список рубрик
│   │   │   └── organizations_spider.py # Паук: организации + отзывы/меню/медиа
│   │   ├── items.py                    # Определения Item-классов
│   │   ├── pipelines.py                # Пайплайн сохранения городов/рубрик
│   │   ├── settings.py                 # Настройки Scrapy
│   │   ├── constants.py                # API URL-шаблоны и поля
│   │   └── utils.py                    # Хелперы: парсинг аргументов, создание запросов
│   ├── converter/                      # Модуль конвертации
│   │   ├── constants.py                # Маппинги контактов, дней недели
│   │   └── utils.py                    # Утилиты: загрузка JSON, парсинг расписания
│   ├── converter.py                    # CLI конвертер JSON → Excel
│   ├── cities_full.json                # Полный список городов (авто)
│   ├── rubrics_full.json               # Полный список рубрик (авто)
│   └── scrapy.cfg                      # Конфигурация Scrapy
├── LICENSE.md   
└── README.md
```

## Параметры паука `organizations`

### Выбор рубрик

| Параметр            | Описание                      | Пример         |
|---------------------|-------------------------------|----------------|
| `rubrics_file`      | Путь к JSON-файлу с рубриками | `rubrics.json` |
| `rubrics_codes`     | Коды рубрик через запятую     | `178,305,652`  |
| `parse_all_rubrics` | Парсить все доступные рубрики | `true`         |

### Выбор городов

| Параметр           | Описание                       | Пример           |
|--------------------|--------------------------------|------------------|
| `cities_file`      | Путь к JSON-файлу с городами   | `cities.json`    |
| `cities_ids`       | ID городов через запятую       | `32,38,42`       |
| `country`          | Код страны (все города страны) | `ru`, `kz`, `cz` |
| `parse_all_cities` | Парсить все доступные города   | `true`           |

### Дополнительные данные

| Параметр        | Описание               | По умолчанию |
|-----------------|------------------------|--------------|
| `parse_reviews` | Собирать отзывы        | `false`      |
| `parse_menus`   | Собирать меню и прайсы | `false`      |
| `parse_media`   | Собирать фото и медиа  | `false`      |

> (!!) В каждой группе (рубрики/города) можно указать **только один** параметр.\
Например, нельзя одновременно использовать `rubrics_file` и `rubrics_codes`.

## Конвертер JSON → Excel

Преобразует собранные JSON-данные в структурированный Excel-файл с колонками:

| Колонка                              | Описание                             |
|--------------------------------------|--------------------------------------|
| ID                                   | Уникальный идентификатор организации |
| Ссылка                               | Ссылка на карточку на 2gis.ru        |
| Название                             | Название организации                 |
| Юр.лицо                              | Юридическое наименование             |
| Рубрики / Основные рубрики           | Категории организации                |
| Страна / Регион / Район / Нас. пункт | Адресная иерархия                    |
| Улица / Дом / Этаж/Офис              | Точный адрес                         |
| Почтовый индекс                      | Индекс                               |
| Широта / Долгота                     | Координаты                           |
| Телефон, Эл.почта, Сайт, ...         | Все виды контактов (20 типов)        |
| Режим работы                         | Расписание по дням                   |
| Рейтинг / Кол-во оценок              | Оценки пользователей                 |
| Инфо                                 | Описание организации                 |

Пустые колонки контактов автоматически удаляются. При конвертации выводится статистика: сколько организаций имеют телефоны, email, количество уникальных контактов по каждому типу.

```bash
python converter.py <input.json> -o <output.xlsx>
```

## Переменные окружения

Создайте `.env` файл в директории `app/`:

```env
# Путь к файлу с полным списком городов (по умолчанию: cities_full.json)
CITIES_FILE=cities_full.json

# Путь к файлу с полным списком рубрик (по умолчанию: rubrics_full.json)
RUBRICS_FILE=rubrics_full.json

# (Опционально) Для ротации прокси
ROTATING_PROXY_LIST_PATH=proxies.txt
```

Для включения прокси установите `PROXY_ENABLED = True` в `app/gis/settings.py`.

## Выходные данные

Результаты сохраняются в `app/data/` в формате JSON с датой в имени файла:

```
data/
├── organizations_2026.02.07.json   # Организации
├── reviews_2026.02.07.json         # Отзывы
├── menus_2026.02.07.json           # Меню
└── media_2026.02.07.json           # Медиа
```

## Основные зависимости

| Название                | Ссылка                                                             |
|-------------------------|--------------------------------------------------------------------|
| Python >= 3.11          | [Ссылка](https://www.python.org/)                                  |
| Scrapy                  | [Ссылка](https://scrapy.org/)                                      |
| python-dotenv           | [Ссылка](https://pypi.org/project/python-dotenv/)                  |
| ijson                   | [Ссылка](https://pypi.org/project/ijson/)                          |
| rv-converter            | [Ссылка](https://github.com/ruvn-1fgas/rv-converter)               |
| scrapy-rotating-proxies | [Ссылка](https://github.com/ruvn-1fgas/scrapy-rotating-proxies)    |

## Лицензия

Код предоставляется **только для некоммерческого использования**\
Подробнее — в [LICENSE.md](LICENSE.md)

**Коммерческая лицензия** может быть предоставлена по запросу - свяжитесь с автором.
