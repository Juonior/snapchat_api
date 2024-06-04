
# <p align="center"><img src="https://www.svgrepo.com/show/303130/snapchat-logo.svg" alt="Snapchat" width="25"/> Snapchat API </p>

## Описание

Данный проект является веб-приложением, разработанным с использованием фреймворка Flask. Он предоставляет API для выполнения различных операций с профилями и фотографиями для расширения [Deluvity Snapchat](https://github.com/Juonior/snapchat_extension)

## Установка

Для установки проекта выполните следующие шаги:

1. Клонируйте репозиторий:
```sh
git clone https://github.com/Juonior/snapchat_api.git
```

2.Перейдите в каталог проекта:

```sh
cd snapchat_api
```
3. Установите зависимости из requirements.txt:
```sh
pip install -r requirements.txt
```

## Использование

После установки проекта запустите его с помощью команды:
```sh
python run.py
```

API будет доступно по адресу http://localhost:5000.

Чтобы развернуть проект на порту 443 для поддержки HTTPS, необходимо выполнить следующие дополнительные шаги:

1. Создайте папку `ssl` в корневой директории проекта.
2. Поместите файлы `cert.pem` и `key.pem` в папку `ssl`. Эти файлы должны содержать сертификат и приватный ключ для HTTPS на порту 443.
3. В файле `main.py` раскомментируйте строку `# app.run(ssl_context=('ssl/cert.pem', 'ssl/key.pem'))` и закомментируйте строку `app.run()`.

Теперь ваше веб-приложение будет доступно по адресу [https://localhost/](https://localhost/). Обратите внимание, что вы можете использовать другие значения для адреса и порта, если это требуется в вашем окружении.

### Endpoints

Проект предоставляет следующие эндпоинты:

- **GET /** - возвращает главную страницу приложения.
- **GET /lastVersion** - возвращает информацию о последней версии приложения.
- **POST /getPhoto** - возвращает фотографию  профиля по идентификатору.
- **POST /getAllProfiles** - возвращает список всех профилей пользователей.
- **POST /getAllPhotos** - возвращает список всех фотографий профиля.
- **POST /deleteAllPhotos** - удаляет все фотографии профиля.
- **POST /deletePhoto** - удаляет фотографии профиля по идентификатору.
- **POST /updateProfile** - обновляет данные профиля по идентификатору.
- **POST /addPhoto** - добавляет фотографию в профиль.
- **POST /createProfile** - создает новый профиль пользователя.
- **POST /getBalance** - возвращает текущий баланс пользователя.
- **POST /checkValidToken** - проверяет валидность токена пользователя.
- **POST /deleteProfile** - удаляет профиль пользователя.

Для каждого эндпоинта необходимо использовать соответствующий метод (GET или POST) и передать необходимые данные в запросе.

## О нас

### Deluvity


Cоздано и поддерживается командой [Deluvity](https://deluvity.ru)

## Контакты

- Вебсайт: [Deluvity](https://deluvity.ru)
- Email: info@deluvity.ru


<div align="center">
    <a href="https://deluvity.com" style="text-decoration: none; color: inherit;">
        <img src="https://i.imgur.com/6SeUsNl.png" alt="Snapchat" width="100"/>
    </a>
</div>
