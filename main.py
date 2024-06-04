from flask import Flask, request, jsonify, render_template, send_file, abort
import os
from flask_cors import CORS
from database import *
from gpt import getAnswer
from crop import resize_image_base64
import logging
from functools import wraps
app = Flask(__name__)
# CORS(app)
CORS(app, resources={r"/*": {"origins": "*"}})

actualVersion = "1.0.5"
downloadPath = "static/Snapchat-BETA-v1.0.5.zip"

# Настройка логирования только в файл
file_handler = logging.FileHandler("app3.log", encoding= 'utf-8')
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)

# Настройка основного логгера
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)



def log_request(f):
    @wraps(f)
    def wrapper(*args, **kwargs):

        # Проверка на наличие ключа 'photos' в JSON-теле запроса

        if request.is_json:

            json_data = request.get_json().copy()  # Создаем копию данных
            if 'photos' in json_data:
                del json_data['photos']  # Удаляем ключ 'photos'

            logger.info(f"Request body: {json_data}")  # Логируем оставшиеся данные

        else:
            logger.info("Request body is not in JSON format")

        response = f(*args, **kwargs)

        # Логирование ответа
        logger.info(f"Response: {response.get_json() if response.is_json else 'Response is not in JSON format'}")

        return response
    
    return wrapper


@app.route('/', methods = ['GET'])
def index():
    return render_template('index.html')

@app.route('/download', methods = ['GET'])
def download():
    if os.path.isfile(downloadPath):
        return send_file(downloadPath, as_attachment=True)
    else:
        abort(404)  # Возвращает ошибку 404, если файл не найден

@app.route('/getAllProfiles', methods = ['POST'])
def getAllProfiles():
    data = request.get_json()

    # проверяем наличие токена в теле запроса
    if "token" not in data:
        return jsonify({"message": "Poor request", "success": False})
    
    token = data["token"]
    if not isValidToken(token):
        return jsonify({"message": "Invalid token", "success": False})
    
    con = sqlite3.connect("profiles.db")
    cur = con.cursor()

    # получаем все строки с текущим токеном
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

    # возвращаем массив из данных о профилях
    return jsonify({"message": profiles, "success": True})


@app.route('/addPhoto', methods = ['POST'])
def addPhoto():
    data = request.get_json()
    checkData = ["token", "profile_id", "photo"]

    # Проверяем наличие profile_id и фото в запросе
    if (len(set(data) & set(checkData))!= 3):
        return jsonify({"message": "Poor request", "success": False})
    
    token = data["token"]
    photo = data["photo"]
    profile_id = data["profile_id"]

    if not isValidToken(token):
        return jsonify({"message": "Invalid token", "success": False})
    
    if not checkProfileToken(profile_id, token):
        return jsonify({"message": "Invalid token for this profile", "success": False})
    
    resizeImage = resize_image_base64(photo)
    if resizeImage == "Incorrect images ratio":
        return jsonify({"message" : resizeImage, "success": False})
    
    return jsonify(addingPhoto(profile_id, resizeImage))


@app.route('/getAllPhotos', methods = ['POST'])
def getAllPhotos():
    data = request.get_json()

    # проверяем наличие id и токена в теле запроса
    if "profile_id" not in data or "token" not in data:
        return jsonify({"message": "Poor request", "success": False})
    
    token = data["token"]
    id = data["profile_id"]

    # проверяем валиден ли токен
    if not isValidToken(token):
        return jsonify({"message": "Invalid token", "success": False})
    
    if not checkProfileToken(id, token):
        return jsonify({"message": "Invalid token for this profile", "success": False})
    
    conn = sqlite3.connect('profiles.db')
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM profiles WHERE id=?", (id,))
    selectID = cursor.fetchone()
    
    if (selectID):
        cursor.execute("SELECT * FROM photos WHERE profile_id = ?", (id,))
        selectPhotos = cursor.fetchall()
        Photos = []
        for i in selectPhotos:
            Photos.append({"id": i[0], "photo": i[2]}) 
        cursor.close()
        conn.close()
        return jsonify({"message": Photos, "success": True})
    
    else:
        cursor.close()
        conn.close()
        return jsonify({"message": "Invalid id", "success": False})
    
@app.route('/deleteAllPhotos', methods = ['POST'])

def deleteAllPhotos():
    data = request.get_json()

    if "token" not in data or "profile_id" not in data:
        return jsonify({"message": "Poor request", "success": False})

    token = data["token"]
    id = data["profile_id"]

    if not isValidToken(token):
        return jsonify({"message": "Invalid token", "success": False})
    
    if not checkProfileToken(id, token):
        return jsonify({"message": "Invalid token for this profile", "success": False})
    
    conn = sqlite3.connect('profiles.db')
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM profiles WHERE id=?", (id,))
    selectProfileID = cursor.fetchone()

    if (selectProfileID):
        cursor.execute("DELETE FROM photos WHERE profile_id = ?", (id,))
        cursor.execute("DELETE FROM countPhotos WHERE profile_id = ?", (id,))

        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Successful delete", "success": True})
    else:

        cursor.close()
        conn.close()
        return jsonify({"message": "Invalid profile ID", "success": False})    
    
@app.route('/deletePhoto', methods = ['POST'])

def deletePhoto():
    data = request.get_json()
    checkdata = ["token", "id", "profile_id"]

    if len(set(data) & set(checkdata)) != 3:
        return jsonify({"message": "Poor request", "success": False})
    
    token = data["token"]
    id = data["id"]
    profileID = data["profile_id"]

    if not isValidToken(token):
        return jsonify({"message": "Invalid token", "success": False})
    
    if not checkProfileToken(id, token):
        return jsonify({"message": "Invalid token for this profile", "success": False})
    
    conn = sqlite3.connect('profiles.db')
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM profiles WHERE id=?", (profileID,))
    selectProfileID = cursor.fetchone()

    cursor.execute("SELECT id FROM photos WHERE id=?", (id,))
    selectID = cursor.fetchone()
    if not(selectProfileID):

        cursor.close()
        conn.close()
        return jsonify({"message": "Invalid profile ID", "success": False})
    elif not(selectID):

        cursor.close()
        conn.close()
        return jsonify({"message": "Invalid photo ID", "success": False})
    else:
        cursor.execute("DELETE FROM photos WHERE id = ?", (id,))

        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Successful delete", "success": True})
    
@app.route('/updateProfile', methods = ['POST'])   
@log_request
def updateProfile():
    
    data = request.get_json()
    checkData = ["id", "name", "modelInfo", "setting", "sourceOfAdds", "age", "city", "link", "cta", "ctaInfo", "ctaMessageNum", "minCooldown", "maxCooldown", "platform","token"]

    if (len(set(data)&set(checkData)) != len(checkData)):
        return jsonify({"message" : "Not enough arguments", "success" : False})
    
    name = data["name"]
    modelInfo = data["modelInfo"]
    setting = data["setting"]
    sourceOfAdds = data["sourceOfAdds"]
    age = data["age"]
    city = data["city"]
    link = data["link"]
    cta = data["cta"]
    ctaInfo = data["ctaInfo"]
    ctaMessageNum = data["ctaMessageNum"]
    minCooldown = data["minCooldown"]
    maxCooldown = data["maxCooldown"]
    platform = data["platform"]
    token = data["token"]
    id = data["id"]

    if not isValidToken(token):
        return jsonify({"message": "Invalid token", "success": False})
    if not checkProfileToken(id, token):
        return jsonify({"message": "Invalid token for this profile", "success": False})
    
    return jsonify(updateInfo(name, modelInfo, setting, sourceOfAdds, age, city, link, cta, ctaInfo, ctaMessageNum, minCooldown, maxCooldown, platform, id))

@app.route('/getBalance', methods = ['POST'])

def getBalance():
    data = request.get_json()

    # Проверяем наличие токена в запросе
    if "token" not in data:
        return jsonify({"message": "Poor request", "success": False})
    
    # Получаем токен
    token = data["token"]

    if isValidToken(token):
        return jsonify(Balance(token))
    
    else:
        return jsonify({"message": "Invalid token", "success": False})
    

@app.route('/getPhoto', methods = ['POST'])
def getPhoto():
    data = request.get_json()
    checkData = ["token","profile_id", "username"]

    # Проверяем наличие profile_id и username в теле запроса
    if (len(set(data) & set(checkData))!= 3):
        return jsonify({"message": "Poor request", "success": False})
    
    token = data["token"]
    profile_id = data["profile_id"]
    username = data["username"]

    if not isValidToken(token):
        return jsonify({"message": "Invalid token", "success": False})
    
    if not checkProfileToken(profile_id, token):
        return jsonify({"message": "Invalid token for this profile", "success": False})
    
    return jsonify(getPhotos(profile_id, username))



@app.route("/checkValidToken", methods = ['POST'])
@log_request
def checkToken():
    data = request.get_json()

    # Проверяем наличие токена в теле запроса
    if "token" not in data:
        return jsonify({"message": "Poor request", "success": False})
    
    token = data["token"]

    if isValidToken(token):
        return jsonify({"message": "Valid token", "success": True})
    
    else:
        return jsonify({"message": "Invalid token", "success": False})

def isValidToken(token):
    conn = sqlite3.connect("profiles.db")
    cursor = conn.cursor()

    # ищем токен в базе данных
    cursor.execute("SELECT balance FROM tokens WHERE token=?", (token,))
    selectBalance = cursor.fetchone()
    conn.close()

    if (selectBalance):
        return True
    else:
        return False

@app.route('/deleteProfile', methods = ['POST'])
@log_request
def deleteProfile():
    data = request.get_json()

    # Проверяем наличие id в теле запроса
    if "id" not in data or "token" not in data:
        return jsonify({"message": "Poor request", "success": False})
    
    id = data["id"]
    token = data["token"]

    if not isValidToken(token):
        return jsonify({"message" : "Invalid token", "success": False})

    if not checkProfileToken(id, token):
        return jsonify({"message": "Invalid token for this profile", "success": False})
    
    return jsonify(delete_profile(id, token))


@app.route('/createProfile', methods = ['POST'])
@log_request
def createProfile():
    data = request.get_json()
    checkData = ["name", "modelInfo", "setting", "sourceOfAdds", "age", "city", "link", "cta", "ctaInfo", "ctaMessageNum", "minCooldown", "maxCooldown", "platform","token", "photos"]

    # Проверяем наличие нужных параметров в теле запроса
    if (len(set(data) & set(checkData))!= len(checkData)):
        return jsonify({"message" : "Not enough arguments", "success" : False})
    
    # Получаем значения из jsons
    name = data["name"]
    modelInfo = data["modelInfo"]
    setting = data["setting"]
    sourceOfAdds = data["sourceOfAdds"]
    age = data["age"]
    city = data["city"]
    link = data["link"]
    cta = data["cta"]
    ctaInfo = data["ctaInfo"]
    ctaMessageNum = data["ctaMessageNum"]
    minCooldown = data["minCooldown"]
    maxCooldown = data["maxCooldown"]
    platform = data["platform"]
    token = data["token"]
    photos = data["photos"]

    # Проверяем валидацию токена
    if not isValidToken(token):
        return jsonify({"message" : "Invalid token", "success": False})
    
    # изменяем соотношение сторон для каждой фотографии
    for i in range(len(photos)):
        resizeImage = resize_image_base64(photos[i])
        if resizeImage != "Incorrect images ratio":
            photos[i] = resizeImage
        else:
            return jsonify({"message" : f"Incorrect images ratio for {i + 1} image.", "success": False})
    
    return jsonify(insert_new_profile(name, modelInfo, setting, sourceOfAdds, age, city, link, cta, ctaInfo, ctaMessageNum, minCooldown, maxCooldown, platform, token, photos))
@app.route('/lastVersion', methods = ['GET'])
def lastVersion():
    return jsonify({"message": actualVersion})
    

@app.route('/getAnswer', methods = ['POST'])
@log_request
def get_answer():
    data = request.get_json()
    checkData = ["messages", "name", "modelInfo", "setting", "sourceOfAdds", "age", "city", "link", "ctaInfo", "platform", "token"]

    # Проверяем наличие нужных параметров в теле запроса
    if len(set(data) & set(checkData)) != len(checkData):
        return jsonify({"message" : "Incorrect params", "success": False})
    
    # Получаем значения из jsons
    messages = data["messages"]
    token = data["token"]
    name = data["name"]
    modelInfo = data["modelInfo"]
    setting = data["setting"]
    sourcheOfAdds = data["sourceOfAdds"]
    age = data["age"]
    city = data["city"]
    link = data["link"]
    ctaInfo = data["ctaInfo"]
    platform = data["platform"]

    # Проверяем валидацию токена
    if not isValidToken(token):
        return jsonify({"message": "Invalid Token", "success": False})

    
    print("- Get Answer from token:",token,)
    print("- Token Balance:", Balance(token)["message"])
    # print(messages)
    # Проводим оплату по токену
    if len(messages) > 0:

        if paymentAnswer(token):

            # Отправляем ответ
            answer = getAnswer(messages, name, modelInfo, setting, sourcheOfAdds, age, city, link, ctaInfo, platform)
            return jsonify({"message": answer, "success" : True})
        
        else:
             
             # Сообщаем об отсутствии средств
             return jsonify({"message": "Insufficient balance", "success": False})
    else:

        return jsonify({"message": "Add at least 1 message", "success" : False})
    
        # Получаем ответ пользователю
    #     if len(messages) > 0:
    #         answer = getAnswer(messages, name, modelInfo, setting, sourcheOfAdds, age, city, link, ctaInfo, platform)
    #     else:
    #         return jsonify({"message": "Add at least 1 message", "success" : False})
    #     
    #     return jsonify({"message": answer, "success" : True})
    # else:
    #     
    #     return jsonify({"message": "Insufficient balance", "success": False})
    
    

if __name__ == '__main__':
   app.run(host='0.0.0.0', port=443, debug=True, ssl_context=('ssl/cert.pem', 'ssl/key.pem'))
