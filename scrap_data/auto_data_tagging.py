import pytesseract
from PIL import Image, ImageOps, ImageEnhance
import os
import cv2
import numpy as np

def preprocess_image(image_path):
    # Open image with Pillow
    image = Image.open(image_path)
    
    # Convert to grayscale
    image = ImageOps.grayscale(image)
    
    # Increase contrast
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2)
    
    # Convert to numpy array
    img_array = np.array(image)
    
    # Apply adaptive thresholding
    threshold = cv2.adaptiveThreshold(
        img_array, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    
    # Denoise
    denoised = cv2.fastNlMeansDenoising(threshold, None, 10, 7, 21)
    
    # Dilate to connect broken parts of digits
    kernel = np.ones((2,2),np.uint8)
    dilated = cv2.dilate(denoised, kernel, iterations = 1)
    
    # Remove small noise
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        if cv2.contourArea(contour) < 50:  # adjust this value as needed
            cv2.drawContours(dilated, [contour], 0, (0,0,0), -1)
    
    return Image.fromarray(dilated)

def perform_ocr(image_path):
    # Preprocess the image
    image = preprocess_image(image_path)
    
    # Perform OCR
    custom_config = r'--oem 3 --psm 10 -c tessedit_char_whitelist=0123456789'
    text = pytesseract.image_to_string(image, config=custom_config)
    
    # Return the recognized text
    return text.strip()

def main():
    image_directory = "images"
    
    with open(os.path.join(image_directory, "data.csv"), "w") as file:
        file.write("Filename,Recognized Text\n")

        for filename in os.listdir(image_directory):
            if filename.endswith(".png"):
                image_path = os.path.join(image_directory, filename)
                recognized_text = perform_ocr(image_path)
                print(f"File: {filename}, Recognized text: {recognized_text}")
                file.write(f"{filename},{recognized_text}\n")

if __name__ == "__main__":
    main()