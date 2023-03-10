import base64


def image_to_data_url(filename):
    with open(filename, 'rb') as f:
        img = f.read()
    return base64.b64encode(img).decode('utf-8')
