import json
from PIL import Image, ImageDraw

with open('elo/101/actors/Field.json', 'r') as json_file:
    field_data = json.loads(json_file.read())

image_bounds = [[-36, -50], [513.4, 712.0]]
map_size = [7200, 5184]

def get_ui_coord(x, z):

    x_b = x + 36
    z_b = z + 50
    new_x = (x_b * map_size[0] / (image_bounds[1][0] - image_bounds[0][0]))
    new_z = (z_b * map_size[1] / (image_bounds[1][1] - image_bounds[0][1]))

    return int(new_x), int(new_z)

def do():

    im = Image.open('elo/FieldTerrain_01^_H.png', 'r')
    im.convert('RGBA')
    draw = ImageDraw.Draw(im)

    for actor in field_data['Actors']:
        if "Lynel" in actor['Actor name']:
            nw = get_ui_coord(actor['Translate']['X'] + actor['Scale']['Min X'], actor['Translate']['Z'] + actor['Scale']['Min Z'])
            se = get_ui_coord(actor['Translate']['X'] + actor['Scale']['Max X'], actor['Translate']['Z'] + actor['Scale']['Max Z'])

            draw.rectangle((nw[0], nw[1], se[0], se[1]), '#66666666')

    im.show()

do()