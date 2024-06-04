from PIL import Image
import io
import base64

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