import pytesseract
from PIL import Image
import os

def perform_ocr(image_path):
    # Open the image
    image = Image.open(image_path)
    
    # Perform OCR
    text = pytesseract.image_to_string(image, config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789')
    
    # Return the recognized text
    return text.strip()

def main():
    image_directory = "images"
    
    with open(os.path.join("images", "data.csv"), "w") as file:
        file.write("Filename,Recognized Text\n")

        for filename in os.listdir(image_directory):
            if filename.endswith(".png"):
                image_path = os.path.join(image_directory, filename)
                recognized_text = perform_ocr(image_path)
                file.write(f"{filename},{recognized_text}\n")

if __name__ == "__main__":
    main()