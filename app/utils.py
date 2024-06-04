from PIL import Image
import io
import base64
import httpx
from openai import OpenAI
from config import CHATGPT_API_KEY, CHATGPT_BASE_PROPMT, PROXY_URL





client = OpenAI(
    api_key=CHATGPT_API_KEY,
    http_client=httpx.Client(proxy=PROXY_URL)
)

def makeSlang(answer):
    replacements = {
    "you": "u",
    "hat about u": "bu",
    "y the way": "tw",
    "hat u doing": "yd",
    "et me know": "mk",
    "about": "ab",
    "+": "",
    "ight now": "n"
    }

    for old, new in replacements.items():
        answer = answer.replace(old, new)

    answer = answer.replace("\n ", "\n")
    return answer


def isEmoji(character):
    emoji_ranges = [
        (0x1F600, 0x1F64F),  # Обычные смайлики
        (0x1F300, 0x1F5FF),  # Различные символы и пиктограммы
        (0x1F680, 0x1F6FF),  # Символы транспорта и карты
        (0x1F1E6, 0x1F1FF),  # Флаги стран мира
    ]
    for emoji_range in emoji_ranges:
        if ord(character) in range(emoji_range[0], emoji_range[1] + 1):
            return True
    return False
def addNewlineAfterEmoji(text):
    new_text = ''
    for char in text:
        new_text += char
        if isEmoji(char):
            new_text += "\n"
    return new_text


def removeExtraChars(text):
    extra_chars = ['🛍','🏀','🏈','💬','⚽','📼','📸','📹','🎥','📺','📽','️','🏝','️','🏖','️','🎬','👓','🎧','🎼','🎹','🌂','🥽','🕶','️','🎮','💍','🧳','💼','🎩','👜','🪖','👒','🎓','⛑','️','👞','👑','🙃','😛','🧐','🤓','🤪','😖','😣','😟','😤','😡','🤬','🤯','🤗','😃','😄','😁','😆','😀','😝','😠','😶','‍','🌫','️','😱','😨','😰','😥','😓','🤗','🤔','🫡','🤫','🫠','🤥','😶','🫥','😬','🫨','😑','🫤','😐','😯','😦','😧','😮','😪','😮','‍','💨','😵','😵','‍','💫','🤐','🥴','🤒','😷','🤧','🤮','🤢','🤕','🤑','🤠','👻','💩','👺','👹','👹','💀','☠','️','👽','👾','🤖','🎃','😾','🙀','🤲','👐','🙌','🤝','👊','✊','🤛','🤜','🫷','🫸','🫰','🤟','🤘','🤌','🏻','🤏','🫳','🫴','👈','👉','🏻','👆','👇','☝','️','✋','🤚','🖐','️','🖖','👋','🤙','🫲','🫱','🦾','💪','🖕','✍','️','🫵','🦶','🦵','🦿','💄','🫦','👄','🦷','👅','👂','🦻','👃','👣','👁','️','🫀','🫁','🗣','️','👤','👥','🫂','🪢','🧶','🧵','🪡','👕','👚','🦺','🥼','🧥','👖','🩲','🩳','👔','👗','🩴','🥻','👘','🩱','👙','🥿','👠','👡','👢','👞','🧣','🧤','🧦','🥾','👟','🎩','🧢','👒','🎓','⛑','️','👛','👝','💍','👑','🪖','👜','💼','🎒','🧳','👓','🥽','🕶','️','🌂','🐱','🐶','🐭','🐹','🐰','🦊','🐻','🐼','🐻','‍','❄','️','🐨','🐯','🦁','🐮','🐷','🐽','🐸','🐒','🐔','🐧','🐦','🐤','🐦','‍','⬛','🦆','🪿','🐥','🐣','🦅','🦉','🦇','🐺','🐗','🪱','🫎','🐝','🦄','🐴','🐛','🐌','🐞','🐜','🦗','🦟','🪳','🪲','🪰','🕷','️','🕸','️','🦂','🐢','🐍','🦑','🐙','🦕','🦖','🦎','🪼','🦐','🦞','🦀','🐡','🐋','🐳','🐬','🐟','🐠','🦈','🦭','🐊','🐅','🐆','🐘','🦣','🦧','🦍','🦓','🦛','🦏','🐪','🐫','🦒','🐄','🐂','🐃','🦬','🦘','🫏','🐎','🐖','🐏','🐑','🐩','🦌','🐕','🐐','🦙','🦮','🐕','‍','🦺','🐈','🐈','‍','⬛','🪶','🦚','🦤','🦃','🐓','🪽','🦜','🦢','🦩','🕊','️','🐇','🦦','🦫','🦡','🦨','🦝','🦥','🐁','🐀','🐿','️','🦔','🎄','🌵','🐲','🐉','🐾','🌲','🌳','🌴','🪵','🌱','🪴','🎍','🍀','☘','️','🌿','🎋','🍃','🍂','🍁','🪺','🪨','🪸','🐚','🍄','🪹','🌾','💐','🌷','🌹','🥀','🌼','🌸','🌺','🪷','🪻','🌻','🌙','💫','⚡','️','✨','🌟','⭐','️','☄','️','☀','️','🌈','🌪','️','💥','🌤','️','⛅','️','🌥','️','☁','️','🌦','️','🌧','️','⛈','️','🌩','️','🌨','️','❄','️','💨','🌬','️','⛄','️','☃','️','🫧','☔','️','☂','️','💧','🌊','🫧','🌫','️','🍿','🍙','🎂','🍺','🥃','🥣','🤿','🥅','🎣','🪃','🏹','🛝','🪁','🥋','⛸','️','🎽','🥌','🛼','🛷','🎟','️','🏵','️','🎗','️','🎫','🤹','🏽','‍','♂','️','🤹','‍','♂','️','🤹','‍','♀','️','🎪','🎤','🎬','🎨','🎭','🩰','🎧','🎼','🎹','🪇','🥁','🎸','🪗','🎺','🎷','🪘','🪕','🎻','🪈','🎲','♟','️','🧩','🎰','🎮','🎳','🎯','🚗','🚕','🚙','🚌','🚎','🚐','🚒','🚑','🚓','🏎','️','🛻','🚚','🚛','🚜','🦯','🚲','🛴','🩼','🦼','🦽','🛵','🏍','️','🛺','🛞','🚨','🚡','🚖','🚘','🚍','🚔','🚠','🚟','🚃','🚋','🚞','🚂','🚈','🚅','🚄','🚝','🚆','🚇','🚊','🚉','✈','️','🛰','️','💺','🛩','️','🛬','🛫','🚀','🛸','🚁','🛶','⛵','️','🚢','⛴','️','🛳','️','🛥','️','🚤','🛟','⚓','️','🪝','⛽','️','⛽','️','🗿','🗺','️','🚏','🚥','🚦','🗽','🗼','🏰','🏯','🏟','️','⛱','️','⛲','️','🎠','🎢','🎡','🏖','️','🏝','️','🏜','️','🌋','⛰','️','🛖','⛺','️','🏕','️','🗻','🏔','️','🏠','🏡','🏘','️','🏚','️','🏗','️','🏤','🏣','🏬','🏢','🏭','🏥','🏦','🏨','🏪','🏫','🕌','⛪','️','🏛','️','💒','🏩','🕍','🛕','🕋','⛩','️','🛤','️','🌅','🏞','️','🎑','🗾','🛣','️','🌄','🌠','🎇','🎆','🌇','🌉','🌌','🌃','🏙','️','🌆','🌁','⌚','️','📱','📲','💻','⌨','️','🕹','️','🖲','️','🖱','️','🖨','️','🖥','️','🗜','️','💽','💾','💿','📀','🎥','📹','📸','📷','📼','📽','️','🎞','️','📞','☎','️','📟','🎚','️','🎙','️','📻','📺','📠','🎛','️','🧭','⏱','️','⏲','️','⏰','🔋','📡','⏳','⌛','️','🕰','️','🪫','🔌','💡','🔦','🕯','️','🪙','🛢','️','🧯','🪔','💳','🪪','💎','⚖','️','🪜','⚒','️','🔨','🪛','🪛','🧰','🛠','️','⛏','️','🔩','⚙','️','🔫','🧲','⛓','️','🧱','🪤','🗡','️','🗡','️','🪓','🧨','💣','⚔','️','🛡','️','🚬','⚰','️','🪦','🧿','📿','🔬','🔭','⚗','️','🏺','💈','⚱','️','🪬','🖼']
    for char in extra_chars:
        text = text.replace(char, '')
    return text

def replaceAny(prompt, name, modelInfo, setting, sourceOfAdds, age, city, link, ctaInfo, platform):
    replacements = {
    "[name]": name,
    "[model info]": modelInfo,
    "[setting]": setting,
    "[source of adds]": sourceOfAdds,
    "[age]": age,
    "[city]": city,
    "[link]": link,
    "[cta info]": ctaInfo,
    "[Platform]": platform
}
    

    for placeholder in replacements:
        prompt = prompt.replace(placeholder, replacements[placeholder])

    return prompt


def getPhoto(snapchatMessages):
    prompt = """Imagine you only know how to say two phrases. If the query is about sending a photo, return the answer: !photo, otherwise "I don't know."
    Your answer MUST CONTAIN ONLY !photo OR "I don't know." Don't forget your message history.
    If a user asks something about your appearance, you send a photo too.
    If they ask you questions but ask for a picture at the end, send a picture.
    If they ask you about sending any photo, return the answer: !photo.
    IF A USER HINTS, MENTIONS SENDING A PHOTO, SEND HIM: !photo.
    SNAP MEANS PHOTO TOO.
    You should only respond !photo when directly asked for a photo, not in other contexts like someone mentioning they will go photograph the forest.
    Respond with "I don't know" when asked to evaluate a photo, look at a photo, or interact with a photo in any other way except sending it.
    """
    messages = [{"role": "system", "content" : prompt}]
    messages += snapchatMessages

    complet = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.8
    )


    ans = complet.choices[0].message.content

    return ans

def getAnswer(message, name, modelInfo, setting, sourceOfAdds, age, city, link, ctaInfo, platform):
    prompt = CHATGPT_BASE_PROPMT
    prompt = replaceAny(prompt, name, modelInfo, setting, sourceOfAdds, age, city, link, ctaInfo, platform)
    
    messages = [{"role" : "system" , "content": prompt}]
    for i in message:
        i["content"] = i["content"].replace("*BotPhoto*", "")
        
    messages += message
    keywords = ["send", "share" ,"photo", "snap", "pic", "picture", "look", "one", "more"]
    includingKeywords = any(keyword in message[-1]["content"].lower() for keyword in keywords)

    if includingKeywords:
        answer = getPhoto(message[-3:])
        if "photo" in answer:
            return "!photo"
    res = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.8
    ) 
    answer = res.choices[0].message.content
    answer = addNewlineAfterEmoji(answer)
    if "Heyy" in answer:
        return "Hey\nhow r u?"
    elif "without sharing photos" in answer.lower():
        return "!photo"
    answer = answer.replace('. ', "\n").replace("! ","\n").replace("? ","?\n").replace("'","")
    if answer[-1] == ".":
        answer = answer[:-1]
    answer = makeSlang(answer)
    return removeExtraChars(answer).lower()
    

def crop_to_phone_resolution(image):
    target_ratio = 9 / 16
    width, height = image.size
    current_ratio = width / height

    if current_ratio > target_ratio:
        new_width = int(height * target_ratio)
        left = (width - new_width) // 2
        right = left + new_width
        top, bottom = 0, height
    else:
        new_height = int(width / target_ratio)
        top = (height - new_height) // 2
        bottom = top + new_height
        left, right = 0, width

    return image.crop((left, top, right, bottom))

def resize_image_base64(image_base64):
    prefix = "data:image/jpeg;base64,"
    if image_base64.startswith(prefix):
        image_base64 = image_base64[len(prefix):]

    image_bytes = base64.b64decode(image_base64)
    img = Image.open(io.BytesIO(image_bytes))
    
    try:
        
        cropped_img = crop_to_phone_resolution(img)
        resized_img = cropped_img.resize((1080, 1920), Image.LANCZOS)
        # Сжимаем фотографию до разрешения 1080x1920
        

        resized_img_bytes = io.BytesIO()
        resized_img.save(resized_img_bytes, format='JPEG')
        resized_img_base64 = base64.b64encode(resized_img_bytes.getvalue()).decode('utf-8')

        return prefix + resized_img_base64
    except Exception:
        return "Incorrect images ratio"