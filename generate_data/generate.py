import os
import random
from PIL import Image, ImageDraw, ImageFont
import csv
from tqdm import tqdm

def generate_image(numbers, image_size=(104, 32), bg_color=(255, 255, 255)):
    image = Image.new('RGB', image_size, bg_color)
    draw = ImageDraw.Draw(image)
    
    total_width = 0
    digit_images = []
    
    for num in numbers:
        font_size = random.randint(24, 32)  # Adjusted font size
        font = ImageFont.truetype("arialbd.ttf", font_size)  # Using Arial Bold
        
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        if color[0] + color[1] + color[2] > 600:  # If the color is too bright
            color = (0, 0, 0)
        
        # Create an image for each digit
        txt_img = Image.new('RGBA', (font_size*2, font_size*2), (255, 255, 255, 0))
        txt_draw = ImageDraw.Draw(txt_img)
        txt_draw.text((font_size//2, font_size//2), str(num), font=font, fill=color)
        
        # Rotate the digit
        rotation = random.uniform(-15, 15)
        txt_img = txt_img.rotate(rotation, expand=1, resample=Image.BICUBIC)
        
        # Crop the rotated image
        bbox = txt_img.getbbox()
        txt_img = txt_img.crop(bbox)
        
        digit_images.append(txt_img)
        total_width += txt_img.width
    
    # Calculate starting x position
    start_x = max(0, (image_size[0] - total_width) // 2)
    
    for digit_img in digit_images:
        # Calculate y position to randomly place the digit vertically
        y_position = random.randint(-5, image_size[1] - digit_img.height + 5)
        
        # Paste the digit onto the main image
        image.paste(digit_img, (start_x, y_position), digit_img)
        start_x += digit_img.width - random.randint(0, 2)  # Reduce gap between digits

    return image

def generate_dataset(num_images, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    
    with open(os.path.join(output_dir, 'data.csv'), 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['image_name', 'numbers'])
        
        for i in tqdm(range(num_images)):
            numbers = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            image = generate_image(numbers)
            
            image_name = f'image_{i+1:04d}.png'
            image_path = os.path.join(output_dir, image_name)
            image.save(image_path)
            
            csv_writer.writerow([image_name, numbers])
    
    print(f"Generated {num_images} images and data.csv in {output_dir}")

# Generate the dataset
generate_dataset(num_images=2000, output_dir=os.path.join('generate_data', 'images'))