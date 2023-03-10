import ImageConvertion
import PIL.Image as Image
import io
import base64

filepath = 'notebook_icon.png'

string_base64 = ImageConvertion.image_to_data_url(filepath)
byte_string = string_base64.encode()

b = base64.b64decode(byte_string)

print(b)
img = Image.open(io.BytesIO(b))
img.show()
