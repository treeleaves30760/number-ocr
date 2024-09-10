import os
import random
from PIL import Image, ImageDraw, ImageFont
import csv

def generate_image(numbers, image_size=(104, 32), bg_color=(255, 255, 255)):
    image = Image.new('RGB', image_size, bg_color)
    draw = ImageDraw.Draw(image)
    
    total_width = 0
    digit_images = []
    
    for num in numbers:
        font_size = random.randint(18, 24)  # Slightly reduced max font size
        font = ImageFont.truetype("arial.ttf", font_size)
        
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        
        # Create an image for each digit
        txt_img = Image.new('RGBA', (font_size, font_size), (255, 255, 255, 0))
        txt_draw = ImageDraw.Draw(txt_img)
        txt_draw.text((0, 0), str(num), font=font, fill=color)
        
        # Rotate the digit
        rotation = random.uniform(-10, 10)
        txt_img = txt_img.rotate(rotation, expand=1)
        
        digit_images.append(txt_img)
        total_width += txt_img.width + 1  # +1 for minimal spacing
    
    # Adjust spacing if total width is too large
    if total_width > image_size[0]:
        scale_factor = image_size[0] / total_width
        for i, img in enumerate(digit_images):
            new_width = int(img.width * scale_factor)
            new_height = int(img.height * scale_factor)
            digit_images[i] = img.resize((new_width, new_height), Image.LANCZOS)
        total_width = sum(img.width for img in digit_images) + 5  # +5 for minimal spacing
    
    # Calculate starting x position to center the numbers
    start_x = (image_size[0] - total_width) // 2
    
    for digit_img in digit_images:
        # Calculate y position to vertically center the digit
        y_position = (image_size[1] - digit_img.height) // 2
        
        # Paste the digit onto the main image
        image.paste(digit_img, (start_x, y_position), digit_img)
        start_x += digit_img.width + 1  # +1 for minimal spacing

    return image

def generate_dataset(num_images, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    
    with open(os.path.join(output_dir, 'data.csv'), 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['image_name', 'numbers'])
        
        for i in range(num_images):
            numbers = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            image = generate_image(numbers)
            
            image_name = f'image_{i+1:04d}.png'
            image_path = os.path.join(output_dir, image_name)
            image.save(image_path)
            
            csv_writer.writerow([image_name, numbers])
    
    print(f"Generated {num_images} images and data.csv in {output_dir}")

# Generate the dataset
generate_dataset(num_images=1000, output_dir=os.path.join('generate_datas', 'images'))