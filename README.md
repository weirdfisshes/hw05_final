# Социальная сеть Yatube
### Описание. 
Социальная сеть Yatube. В ней можно зарегистрироваться, пройти авторизацию, публиковать посты и подписываться на авторов. Автор: Бурцев Никита. Python 3, Django 2.2.19, SQLite3, Git.

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
source venv/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip

pip install -r requirements.txt
```

Выполнить миграции:

```
python3 hw05_final/manage.py migrate
```

Запустить проект:

```
python3 hw05_final/manage.py runserver
```

