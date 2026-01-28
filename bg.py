from PIL import Image

img = Image.open('/data1/lcy/projects/Space-Time-Pilot/assets/logo.png')
if img.mode == 'RGBA':
    background = Image.new('RGBA', img.size, (255, 255, 255, 255))
    background.paste(img, mask=img.split()[3])
    background.convert('RGB').save('/data1/lcy/projects/Space-Time-Pilot/assets/logo.png')
else:
    img.save('/data1/lcy/projects/Space-Time-Pilot/assets/logo.png')
print('Done')