# api_yamdb
### Описание. 
Социальная сеть Yatube. В ней можно зарегистрироваться, пройти авторизацию, публиковать посты и подписываться на авторов. Автор: Бурцев Никита. Технологии: Django, Django ORM

### Как запустить проект.

Клонировать репозиторий и перейти в него в командной строке:

```
git clone <cсылка_на_проект_в_git>
cd hw05_final

```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

```
source env/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip

pip install -r requirements.txt
```

Выполнить миграции:

```
python3  api_yamdb/manage.py migrate
```

Запустить проект:

```
python3 ьanage.py runserver
```

