from PIL import Image, ImageDraw, ImageFont
import os

# Create a simple test image
def create_test_image():
    # Create a 400x300 image with a blue background
    img = Image.new('RGB', (400, 300), color='lightblue')
    draw = ImageDraw.Draw(img)
    
    # Add some text
    try:
        # Try to use a default font
        font = ImageFont.load_default()
    except:
        font = None
    
    # Draw text
    text = "Bethel Test Image\nUploaded via ImageKit"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Center the text
    x = (400 - text_width) // 2
    y = (300 - text_height) // 2
    
    draw.text((x, y), text, fill='darkblue', font=font)
    
    # Save the image
    img.save('test_image.jpg', 'JPEG')
    print("✅ Test image created: test_image.jpg")
    return 'test_image.jpg'

if __name__ == "__main__":
    create_test_image() 