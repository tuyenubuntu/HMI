from PIL import Image

def convert_to_ico(input_image, output_image):
    """
    Chuyển đổi hình ảnh sang định dạng ICO.

    Args:
        input_image (str): Đường dẫn đến hình ảnh đầu vào (JPG hoặc PNG).
        output_image (str): Đường dẫn đến hình ảnh đầu ra (ICO).
    """

    try:
        # Mở hình ảnh
        img = Image.open(input_image)

        # Chuyển đổi sang định dạng ICO
        img.save(output_image, format="ICO", sizes=[(32, 32)])

        print(f"Đã chuyển đổi {input_image} thành {output_image} thành công!")
    except Exception as e:
        print(f"Lỗi trong quá trình chuyển đổi: {e}")

if __name__ == "__main__":
    input_file = "icon2.png"  
    
    output_file = "icon2.ico"  
    
    convert_to_ico(input_file, output_file)