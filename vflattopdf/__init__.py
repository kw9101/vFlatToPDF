import os
import shutil
import sqlite3
from PIL import Image, ImageDraw
from reportlab.pdfgen import canvas
from pyclovaocr import ClovaOCR
from hanspell import spell_checker

# JPG 파일 경로 목록 설정
jpg_files = [
    './out/두두/0.jpg',
    './out/두두/1.jpg',
    './out/두두/2.jpg',
    './out/두두/3.jpg',
    './out/두두/4.jpg',
    # 추가 이미지 파일 경로들을 여기에 나열
]

# PDF 파일 이름 설정
pdf_file = '두두.pdf'

# 이미지를 PDF로 변환
def images_to_pdf(input_images, output_pdf):
    c = canvas.Canvas(output_pdf, pagesize=Image.open(input_images[0]).size)
    for image_path in input_images:
        c.drawImage(image_path, 0, 0)
        c.showPage()
    c.save()

def trim(image_path, output_path, threshold=0):
    # 이미지 열기
    img = Image.open(image_path)

    # 이미지 주변의 여백을 자르기
    img = img.crop(img.getbbox())

    # 임계값(threshold)보다 작은 픽셀 값 제거 (옵션)
    if threshold > 0:
        img = img.point(lambda p: p > threshold and 255)

    # 결과 이미지 저장
    img.save(output_path)

def draw_red_box(input_image_path, output_image_path):
    # 이미지 열기
    image = Image.open(input_image_path)

    # 이미지 내에서 실제 내용을 둘러싼 바운딩 박스 좌표 얻기
    bbox = image.getbbox()

    # 이미지에 그릴 도구 생성
    draw = ImageDraw.Draw(image)

    # 빨간색 박스 그리기
    draw.rectangle(bbox, outline="red", width=3)

    # 결과 이미지 저장
    image.save(output_image_path)

def crop_image(input_image_path, output_image_path, top, bottom, left, right):
    # 이미지 열기
    image = Image.open(input_image_path)

    # 이미지 자르기
    width, height = image.size
    cropped_image = image.crop((left, top, width - right, height - bottom))

    # 결과 이미지 저장
    cropped_image.save(output_image_path)

def apply_threshold(input_image_path, output_image_path, threshold):
    # 이미지 열기
    image = Image.open(input_image_path)

    # 이미지를 흑백으로 변환
    grayscale_image = image.convert('L')

    inverted_image = grayscale_image.point(lambda p: 255 - p)

    # 임계값 이하의 픽셀 값을 0으로 설정
    thresholded_image = inverted_image.point(lambda p: p > threshold and 255)

    # 결과 이미지 저장
    thresholded_image.save(output_image_path)

if __name__ == '__main__':
    # input_image = './out/두두/4.jpg'  # 입력 JPG 이미지 파일 경로
    # ocr = ClovaOCR()

    # result = ocr.run_ocr(
    #     image_path = input_image,
    #     language_code = 'ko',
    #     ocr_mode = 'general',
    # )

    # text = ''
    # for word in result['words']:
    #     text += word['text'] + ' '

    # print(text)

    spelled_sent = spell_checker.check("맞춤법 틀리면 외 않되? 쓰고싶은대로쓰면돼지 ")
    print(spelled_sent)
    # spelled_sent = spell_checker.check(text)
    # checked_sent = spelled_sent.checked
    # print(checked_sent)
    # threshold_image = './out/두두/4_threshod.jpg'  # 결과 이미지 파일 경로
    # apply_threshold(input_image, threshold_image, 50)

    # croped_image = './out/두두/4_crop.jpg'
    # crop_image(threshold_image, croped_image, 100, 100, 80, 80)
    # draw_red_box(croped_image, './out/두두/4_redbox.jpg')
    # trim(input_image, output_image)

# if __name__ == "__main__":
#     db_path = './vFlat/bookshelf.db'
#     # SQLite 데이터베이스에 연결
#     with sqlite3.connect(db_path) as connection:
#         # 커서 생성
#         cursor = connection.cursor()

#         # 테이블 목록 가져오기
#         # cursor.execute("SELECT path, page_no FROM page;")
#         cursor.execute("SELECT id, title, cover FROM book;")
#         books = cursor.fetchall()

#     for book in books:
#         book_id = book[0]
#         book_title = book[1]
#         book_cover = book[2]

#         print(book_id, book_title, book_cover)

#     # SQLite 데이터베이스에 연결
#     with sqlite3.connect(db_path) as connection:
#         # 커서 생성
#         cursor = connection.cursor()

#         # 테이블 목록 가져오기
#         cursor.execute("SELECT path, page_no FROM page WHERE path LIKE '/book_2%';")
#         pages = cursor.fetchall()

#     for page in pages:
#         page_path = f'./vFlat/{page[0]}'

#         page_no = int(page[1])

#         new_file_name = f'./out/{book_title}/{page_no}.jpg'

#         os.makedirs(os.path.dirname(new_file_name), exist_ok=True)

#         shutil.copy(page_path, new_file_name)

#         print(page_path, page_no)


#     images_to_pdf(jpg_files, pdf_file)