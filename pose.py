from PIL import Image
import os

input_dir = '/data1/lcy/projects/Space-Time-Pilot/assets/pose_vis'
output_dir = '/data1/lcy/projects/Space-Time-Pilot/assets/pose_vis_processed'
os.makedirs(output_dir, exist_ok=True)

for i in range(1, 11):
    input_path = os.path.join(input_dir, f'{i}.png')
    output_path = os.path.join(output_dir, f'{i}.png')

    img = Image.open(input_path)
    width, height = img.size

    # 中心裁剪成正方形
    min_dim = min(width, height)
    left = (width - min_dim) // 2
    top = (height - min_dim) // 2
    right = left + min_dim
    bottom = top + min_dim
    img_cropped = img.crop((left, top, right, bottom))

    # 缩放到 150x150
    img_resized = img_cropped.resize((150, 150), Image.LANCZOS)
    img_resized.save(output_path)
    print(f'Processed {i}.png')

print('Done!')