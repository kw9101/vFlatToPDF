import os
import shutil
import sqlite3
from pprint import pprint
from PIL import Image, ImageDraw
from reportlab.pdfgen import canvas
# from pyclovaocr import ClovaOCR
import easyocr

# 이미지를 PDF로 변환
def images_to_pdf(input_images, output_pdf):
    c = canvas.Canvas(output_pdf, pagesize=Image.open(input_images[0]).size)
    for image_path in input_images:
        c.drawImage(image_path, 0, 0)
        c.showPage()
    c.save()

def find_crop_files(directory):
    crop_files = []  # `_crop.jpg`로 끝나는 파일을 저장할 리스트

    # 디렉토리 내의 모든 파일과 디렉토리를 순회
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith("_crop.jpg"):
                # 파일 이름이 `_crop.jpg`로 끝나면 리스트에 추가
                crop_files.append(os.path.join(root, file))

    return sorted(crop_files)


def draw_red_box(input_image_path, output_image_path, bbox=None):
    # 이미지 열기
    image = Image.open(input_image_path)

    # 이미지 내에서 실제 내용을 둘러싼 바운딩 박스 좌표 얻기
    # bbox = image.getbbox()

    # 이미지에 그릴 도구 생성
    draw = ImageDraw.Draw(image)

    # 빨간색 박스 그리기
    draw.rectangle(bbox, outline="red", width=3)

    # 결과 이미지 저장
    image.save(output_image_path)

def crop_image(input_image_path, output_image_path, bbox):
    # 이미지 열기
    image = Image.open(input_image_path)

    # 이미지 자르기
    cropped_image = image.crop(bbox)

    # 결과 이미지 저장
    cropped_image.save(output_image_path)


def calculate_total_bbox(bboxes):
    # 모든 바운딩 박스를 포함하는 최소 크기의 바운딩 박스의 초기 값 설정
    total_left = float('inf')
    total_top = float('inf')
    total_right = float('-inf')
    total_bottom = float('-inf')

    for bbox in bboxes:
        left, top = bbox[0][0], bbox[1][1]
        right, bottom = bbox[2][0], bbox[2][1]

        # 최소값과 최대값 갱신
        total_left = min(total_left, left)
        total_top = min(total_top, top)
        total_right = max(total_right, right)
        total_bottom = max(total_bottom, bottom)

    # 모든 바운딩 박스를 포함하는 최소 크기의 바운딩 박스 계산
    total_bbox = [[total_left, total_top], [total_right, total_top], [total_right, total_bottom], [total_left, total_bottom]]

    # print("Total Bounding Box:", total_bbox)
    return (total_left, total_top, total_right, total_bottom)

def find_enclosing_bbox(bboxes):
    if not bboxes:
        return None  # 빈 리스트면 None 반환
    
    # bboxes = bboxes[:-1] # 페이지 숫자 제거
    # 초기 최소/최대 좌표 설정
    left = min(b[0] for b in bboxes)
    right = max(b[1] for b in bboxes)
    top = min(b[2] for b in bboxes)
    bottom = max(b[3] for b in bboxes)
    
    # 모든 바운딩 박스를 포함하는 최소 바운딩 박스 좌표 반환
    enclosing_bbox = [left, top, right, bottom]
    return enclosing_bbox

def after_proc(reader, input_image, output_image, space=100):
    # # clovaocr
    # # ocr = ClovaOCR()
    # # result = ocr.run_ocr(
    # #     image_path = input_image,
    # #     language_code = 'ko',
    # #     ocr_mode = 'general',
    # # )
    # # bounding_boxes = [line['boundingBox'] for line in result['lines']]

    # # easyocr
    # reader = easyocr.Reader(['ko', 'en'])

    # readtext
    # result = reader.readtext(input_image)
    # bounding_boxes = [line[0] for line in result]
    # tbbox = calculate_total_bbox(bounding_boxes)

    # detect
    result = reader.detect(input_image)
    bounding_boxes = result[0][0]
    if not bounding_boxes:
        return
    
    tbbox = find_enclosing_bbox(bounding_boxes)

    tbbox = (tbbox[0] - space, tbbox[1] - space, tbbox[2] + space, tbbox[3])
    crop_image(input_image, output_image, tbbox)


if __name__ == "__main__":
    db_path = './vFlat/bookshelf.db'
    # SQLite 데이터베이스에 연결
    with sqlite3.connect(db_path) as connection:
        # 커서 생성
        cursor = connection.cursor()

        # 테이블 목록 가져오기
        # cursor.execute("SELECT path, page_no FROM page;")
        cursor.execute("SELECT id, title, cover FROM book;")
        books = cursor.fetchall()

    select_book_index = 0
    book = books[select_book_index]
    book_id = book[0]
    book_title = book[1]
    book_cover = book[2]

    print(book_id, book_title, book_cover)

    # # SQLite 데이터베이스에 연결
    # with sqlite3.connect(db_path) as connection:
    #     # 커서 생성
    #     cursor = connection.cursor()

    #     # 테이블 목록 가져오기
    #     cursor.execute(f"SELECT path, page_no FROM page WHERE path LIKE '/book_{book_id}/%';")
    #     pages = cursor.fetchall()

    # # easyocr
    # reader = easyocr.Reader(['ko', 'en'])

    # for page in pages:
    #     page_path = f'./vFlat/{page[0]}'

    #     page_no = int(page[1])

    #     new_file_name = f'./out/{book_title}/{page_no:04}.jpg'

    #     print(page_path, page_no, new_file_name)

    #     os.makedirs(os.path.dirname(new_file_name), exist_ok=True)

    #     shutil.copy(page_path, new_file_name)

    #     after_file_name = f'./out/{book_title}/{page_no:04}_crop.jpg'
    #     after_proc(reader, new_file_name, after_file_name)

    jpg_files = find_crop_files(f'./out/{book_title}/')
    pprint(jpg_files)
    pdf_file = f'./out/{book_title}.pdf'
    images_to_pdf(jpg_files, pdf_file)