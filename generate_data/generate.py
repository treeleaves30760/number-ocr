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
        font_size = random.randint(20, 28)  # Adjusted font size
        font = ImageFont.truetype("arial.ttf", font_size)  # Using regular Arial
        
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        if color[0] + color[1] + color[2] > 600:  # If the color is too bright
            color = (0, 0, 0)
        
        # Create an image for each digit
        txt_img = Image.new('RGBA', (font_size*2, font_size*2), (255, 255, 255, 0))
        txt_draw = ImageDraw.Draw(txt_img)
        txt_draw.text((font_size//2, font_size//2), str(num), font=font, fill=color)
        
        # Rotate the digit
        rotation = random.uniform(-10, 10)
        txt_img = txt_img.rotate(rotation, expand=1, resample=Image.BICUBIC)
        
        # Crop the rotated image
        bbox = txt_img.getbbox()
        txt_img = txt_img.crop(bbox)
        
        digit_images.append(txt_img)
        total_width += txt_img.width
    
    # Adjust spacing if total width is too large
    if total_width > image_size[0] - 10:  # Leave 10px margin
        scale_factor = (image_size[0] - 10) / total_width
        for i, img in enumerate(digit_images):
            new_width = int(img.width * scale_factor)
            new_height = int(img.height * scale_factor)
            digit_images[i] = img.resize((new_width, new_height), Image.LANCZOS)
        total_width = sum(img.width for img in digit_images)
    
    # Calculate starting x position
    start_x = max(5, (image_size[0] - total_width) // 2)
    
    for digit_img in digit_images:
        # Calculate y position to randomly place the digit vertically
        max_y = image_size[1] - digit_img.height
        y_position = random.randint(0, max_y)
        
        # Paste the digit onto the main image
        image.paste(digit_img, (start_x, y_position), digit_img)
        start_x += digit_img.width + random.randint(0, 2)  # Small random gap

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