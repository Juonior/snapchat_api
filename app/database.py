import os
from flask import current_app
import sqlite3

actualVersion = "1.0.5"
downloadPath = "static/Snapchat-BETA-v1.0.5.zip"
costAnswer = 0.1

def create_profile_tables():
    db_path = os.path.join(current_app.instance_path, "profiles.db")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Создаем таблицу профилей, если она не существует
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS tokens (
            token TEXT PRIMARY KEY,
            expire TEXT,
            balance INTEGER
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY,
            name TEXT,
            modelInfo TEXT,
            setting TEXT,
            sourceOfAdds TEXT,
            age TEXT,
            city TEXT,
            link TEXT,
            cta TEXT,
            ctaInfo TEXT,
            ctaMessageNum INTEGER,
            minCooldown INTEGER,
            maxCooldown INTEGER,
            platform TEXT,
            token TEXT,
            FOREIGN KEY(token) REFERENCES tokens(token)
        )''')

    # Создаем таблицу фотографий
    cursor.execute('''CREATE TABLE IF NOT EXISTS photos (
            id INTEGER PRIMARY KEY,
            profile_id INTEGER,
            base64_data TEXT,
            FOREIGN KEY(profile_id) REFERENCES profiles(id)
        )''')
    
    # Создаем таблицу количества отправок фото для каждого пользователя
    cursor.execute('''CREATE TABLE IF NOT EXISTS countPhotos (
            id INTEGER PRIMARY KEY,
            username TEXT,
            profile_id INTEGER,
            count INTEGER,
            FOREIGN KEY(profile_id) REFERENCES profiles(id)
        )''')
    
    conn.commit()
    cursor.close()
    conn.close()

def getProfilesByToken(token):
    db_path = os.path.join(current_app.instance_path, "profiles.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Получаем все строки с текущим токеном
    cur.execute("SELECT * FROM profiles WHERE token=?", (token,))
    arrayProfiles = cur.fetchall()
    
    column_names = [
        "id",
        "name",
        "modelInfo",
        "setting",
        "sourceOfAdds",
        "age",
        "city",
        "link",
        "cta",
        "ctaInfo",
        "ctaMessageNum",
        "minCooldown",
        "maxCooldown",
        "platform",
        "token"
    ]
    
    profiles = []
    for i in arrayProfiles:
        profile = {}
        for j in range(len(arrayProfiles[0])):
            profile[column_names[j]] = i[j]
        profiles.append(profile)
    
    conn.close()
    return profiles
def getPhotos(profile_id : int, username : str):
    db_path = os.path.join(current_app.instance_path, "profiles.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM countPhotos WHERE username = ? AND profile_id = ?", (username, profile_id))
    selectUser = cursor.fetchone()
    # Создаем ключ для нового пользователя
    if not(selectUser):
        cursor.execute("INSERT INTO countPhotos (username, profile_id, count) VALUES (?, ?, 0)", (username, profile_id))
        conn.commit()

    cursor.execute("SELECT base64_data FROM photos WHERE profile_id = ?", (profile_id,))
    photos = cursor.fetchall()
    if not(photos):
        return {"message" : "Photo not exist for profile", "success" : False}
    
    # Определяем количество отправок фото для текущего пользователя
    cursor.execute("SELECT count FROM countPhotos WHERE username = ? AND profile_id = ?", (username, profile_id))
    count = cursor.fetchone()[0]
    length = len(photos)
    # Обнуляем количество при переполнении
    if count + 1 == length:
        cursor.execute("UPDATE countPhotos SET count = ? WHERE username = ? AND profile_id = ?", (0, username, profile_id))
        photo = photos[-1]
    elif count + 1 > length: 
        cursor.execute("UPDATE countPhotos SET count = ? WHERE username = ? AND profile_id = ?", (1, username, profile_id))
        photo = photos[0]
    else:
        cursor.execute("UPDATE countPhotos SET count = ? WHERE username = ? AND profile_id = ?", (count + 1, username, profile_id))
        photo = photos[count]

    conn.commit()
    cursor.close()
    conn.close()

    return {"message" : photo, "success" : True}

def checkProfileToken(profile_id: int, requestToken: str):
    try:
        # Подключение к базе данных
        db_path = os.path.join(current_app.instance_path, "profiles.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Проверка наличия профиля с заданным id и получение токена
        cursor.execute("SELECT token FROM profiles WHERE id=?", (profile_id,))
        result = cursor.fetchone()

        if result is None:
            return False

        stored_token = result[0]

        # Проверка совпадения токенов
        return stored_token == requestToken
    
    except sqlite3.Error as e:
        # Логирование ошибки базы данных, если необходимо
        print(f"Database error: {e}")
        return False
    
    finally:
        if conn:
            conn.close()

def insert_new_profile(*args):
    if len(list(args)) != 15:
        return {"message": f"Got {len(list(args))} values. Need 15.", "success" : False}
    db_path = os.path.join(current_app.instance_path, "profiles.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Вставляем данные о профиле в базу данных
    cursor.execute('''INSERT INTO profiles (name, 
                   modelInfo, 
                   setting, 
                   sourceOfAdds, 
                   age, 
                   city, 
                   link, 
                   cta, 
                   ctaInfo, 
                   ctaMessageNum, 
                   minCooldown, 
                   maxCooldown,
                   platform, 
                   token) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (args[:-1]))
    
    # Получаем id вставленного профиля
    profile_id = cursor.lastrowid
    photos = args[-1]

    for photo in photos:
        cursor.execute("INSERT INTO photos (base64_data, profile_id) VALUES (?, ?)", (photo, profile_id))

    conn.commit()
    cursor.close()
    conn.close()

    return {"message": "Success insert", "success" : True}

def addingPhoto(id: int, photo: str):
    db_path = os.path.join(current_app.instance_path, "profiles.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # проверяем, что текущий профиль существует
    cursor.execute("SELECT id FROM profiles WHERE id=?", (id,))
    selectID = cursor.fetchone()

    if (selectID):
        cursor.execute("INSERT INTO photos (base64_data, profile_id) VALUES (?, ?)", (photo, id))
        conn.commit()
        cursor.close()
        conn.close()
        return {"message": "Success adding", "success" : True}
    else:
        cursor.close()
        conn.close()
        return {"message": "Profile not found", "success": False}

def delete_profile(id: int, token: str):
    db_path = os.path.join(current_app.instance_path, "profiles.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Получаем id профиля
    cursor.execute("SELECT id FROM profiles WHERE id=?", (id,)) 
    selectID = cursor.fetchone()
    
    if (selectID):
        selectID = selectID[0]
        cursor.execute("DELETE FROM profiles WHERE id=? AND token=?", (id,token))

        # Проверяем, что существовал такой профиль с данными id и token
        if cursor.rowcount > 0:
            cursor.execute("DELETE FROM photos WHERE profile_id=?", (id,))
            cursor.execute("DELETE FROM countPhotos WHERE profile_id=?", (id,))

            # Применяем изменения
            conn.commit()
            cursor.close()
            conn.close()

            return {"message": "Profile success deleted", "success": True}
        
        else:

            return {"message": "Invalid token for this profile", "success": False}
    
    else:
        cursor.close()
        conn.close()
        return {"message": "Profile not found", "success": False}

def updateInfo(*arg):
    db_path = os.path.join(current_app.instance_path, "profiles.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Вставляем данные о профиле в базу данных
    cursor.execute('''UPDATE profiles SET name = ?, 
                   modelInfo = ?, 
                   setting = ?, 
                   sourceOfAdds = ?, 
                   age = ?, 
                   city = ?, 
                   link = ?, 
                   cta = ?, 
                   ctaInfo = ?, 
                   ctaMessageNum = ?, 
                   minCooldown = ?, 
                   maxCooldown = ?,
                   platform = ? WHERE id = ? ''',
                    (arg))
    
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "Successful update", "success": True}

def Balance(token):
    db_path = os.path.join(current_app.instance_path, "profiles.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Получаем баланс токена
    cursor.execute("SELECT balance FROM tokens WHERE token=?", (token,))
    balance = cursor.fetchone()[0]

    cursor.close()
    conn.close()
    return {"message": balance, "success" : True}

def paymentAnswer(token):
    db_path = os.path.join(current_app.instance_path, "profiles.db")
    # Получаем текущий баланс токена
    balance = Balance(token)["message"]

    newBalance = balance - costAnswer
    newBalance = round(newBalance, 2)

    # Отклоняем транзакцию, если на балансе недостаточно средств
    if newBalance < 0:
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("UPDATE tokens SET balance = ? WHERE token=?", (newBalance, token))

    conn.commit()
    cursor.close()
    conn.close()
    return True

def isValidToken(token):
    db_path = os.path.join(current_app.instance_path, "profiles.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # ищем токен в базе данных
    cursor.execute("SELECT balance FROM tokens WHERE token=?", (token,))
    selectBalance = cursor.fetchone()
    conn.close()

    if (selectBalance):
        return True
    else:
        return False
    

def db_init(app):
    with app.app_context():
        create_profile_tables()

