from flask import Blueprint, request, jsonify, render_template, send_file, abort
from app.database import *
from app.utils import getAnswer, resize_image_base64
import logging
from functools import wraps

logger = logging.getLogger(__name__)

def log_request(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if request.is_json:
            json_data = request.get_json().copy()
            if 'photos' in json_data:
                del json_data['photos']
            logger.info(f"Request body: {json_data}")
        else:
            logger.info("Request body is not in JSON format")
        response = f(*args, **kwargs)
        logger.info(f"Response: {response.get_json() if response.is_json else 'Response is not in JSON format'}")
        return response
    return wrapper

bp = Blueprint('routes', __name__)

@bp.route('/', methods = ['GET'])
def index():
    return render_template('main.html')

@bp.route('/download', methods = ['GET'])
def download():
    return send_file(downloadPath, as_attachment=True)


@bp.route('/getAllProfiles', methods=['POST'])
def getAllProfiles():
    data = request.get_json()

    # Проверяем наличие токена в теле запроса
    if "token" not in data:
        return jsonify({"message": "Poor request", "success": False})
    
    token = data["token"]
    if not isValidToken(token):
        return jsonify({"message": "Invalid token", "success": False})
    
    profiles = getProfilesByToken(token)

    # Возвращаем массив из данных о профилях
    return jsonify({"message": profiles, "success": True})


@bp.route('/addPhoto', methods = ['POST'])
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


@bp.route('/getAllPhotos', methods=['POST'])
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

    selectID = get_profile_id(id)

    if selectID:
        selectPhotos = get_photos(id)
        Photos = [{"id": i[0], "photo": i[2]} for i in selectPhotos]
        return jsonify({"message": Photos, "success": True})
    else:
        return jsonify({"message": "Invalid id", "success": False})

@bp.route('/deleteAllPhotos', methods=['POST'])
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

    selectProfileID = get_profile_id(id)

    if selectProfileID:
        delete_photos(id)
        return jsonify({"message": "Successful delete", "success": True})
    else:
        return jsonify({"message": "Invalid profile ID", "success": False})
    
@bp.route('/deletePhoto', methods=['POST'])
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

    if not checkProfileToken(profileID, token):
        return jsonify({"message": "Invalid token for this profile", "success": False})

    selectProfileID = get_profile_id(profileID)
    selectID = get_photo_id(id)

    if not selectProfileID:
        return jsonify({"message": "Invalid profile ID", "success": False})
    elif not selectID:
        return jsonify({"message": "Invalid photo ID", "success": False})
    else:
        delete_photo(id)
        return jsonify({"message": "Successful delete", "success": True})
    
@bp.route('/updateProfile', methods = ['POST'])   
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

@bp.route('/getBalance', methods = ['POST'])

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
    

@bp.route('/getPhoto', methods = ['POST'])
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



@bp.route("/checkValidToken", methods = ['POST'])
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


@bp.route('/deleteProfile', methods = ['POST'])
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


@bp.route('/createProfile', methods = ['POST'])
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
@bp.route('/lastVersion', methods = ['GET'])
def lastVersion():
    return jsonify({"message": actualVersion})
    

@bp.route('/getAnswer', methods = ['POST'])
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

def register_routes(app):
    app.register_blueprint(bp)
