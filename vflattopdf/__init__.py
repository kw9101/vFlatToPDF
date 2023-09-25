import os
import shutil
import sqlite3
from pprint import pprint
from PIL import Image, ImageDraw
from reportlab.pdfgen import canvas
# from pyclovaocr import ClovaOCR
import easyocr
from tqdm import tqdm
import time

# 이미지를 PDF로 변환
def images_to_pdf(input_images, output_pdf):
    c = canvas.Canvas(output_pdf, pagesize=Image.open(input_images[0]).size)
    for image_path in tqdm(input_images, desc="pdf", ncols=100):
        c.drawImage(image_path, 0, 0)
        c.showPage()
    c.save()


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


def copy_vflat_to_out(pages, output_folder):
    # 출력 폴더가 없으면 생성
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    out_page_paths = []
    for page in tqdm(pages, desc="copy", ncols=100): # vflat page 를 page 번호 순서대로 out 폴더에 복사
        page_path = f'./vFlat{page[0]}'
        page_no = int(page[1])
        out_page_path = f'{output_folder}/{page_no:04}.jpg'
        shutil.copy(page_path, out_page_path)
        out_page_paths.append(out_page_path)

    return out_page_paths


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


def crop_images_by_text(pages, output_folder, space = 100):
    # 출력 폴더가 없으면 생성
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # clovaocr
    # ocr = ClovaOCR()
    # result = ocr.run_ocr(
    #     image_path = input_image,
    #     language_code = 'ko',
    #     ocr_mode = 'general',
    # )
    # bounding_boxes = [line['boundingBox'] for line in result['lines']]

    # easyocr
    reader = easyocr.Reader(['ko', 'en'], gpu=True)

    # readtext
    # result = reader.readtext(input_image)
    # bounding_boxes = [line[0] for line in result]
    # tbbox = calculate_total_bbox(bounding_boxes)

    crop_pages = []
    for page in tqdm(pages, desc="crop", ncols=100):
        # detect
        result = reader.detect(page)
        bounding_boxes = result[0][0]
        if not bounding_boxes:
            continue

        tbbox = find_enclosing_bbox(bounding_boxes)

        # tbbox = (tbbox[0] - space, tbbox[1], tbbox[2] + space, tbbox[3])
        left = tbbox[0] - space
        top = tbbox[1] - space * 0.5 # tbbox[1], 위 쪽은 일정하게 자른다.
        right = tbbox[2] + space
        bottom = tbbox[3] + 10 # 보통 페이지를 표시한다. 바로 자른다.

        crop_page_path = os.path.splitext(os.path.basename(page))[0] + '_crop.jpg'
        crop_page_path = os.path.join(output_folder, crop_page_path)
        crop_image(page, crop_page_path, (left, top, right, bottom))
        crop_pages.append(crop_page_path)

    return crop_pages


def normalize_images_to_reference(reference_image_path, pages, output_folder):
    # 기준 이미지 열기
    reference_image = Image.open(reference_image_path)
    reference_width = reference_image.size[0]  # 기준 이미지의 너비
    reference_height = reference_image.size[1]  # 기준 이미지의 높이

    # 출력 폴더가 없으면 생성
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    nomalize_pages = []
    # 이미지 크기를 기준 이미지의 높이에 맞게 조정
    for page in tqdm(pages, desc="normalize", ncols=100):
        # 이미지 열기
        img = Image.open(page)

        img_width = img.size[0]
        img_height = img.size[1]

        ratio_by_width = reference_width / img_width
        ratio_by_height = reference_height / img_height
        normalize_img = img.resize((int(img.width * ratio_by_width), int(img.height * ratio_by_height)), Image.LANCZOS)

        # 새로 조정된 이미지를 저장
        normalize_page_path = os.path.splitext(os.path.basename(page))[0] + '_normalized.jpg'
        normalize_page_path = os.path.join(output_folder, normalize_page_path)
        normalize_img.save(normalize_page_path)

        nomalize_pages.append(normalize_page_path)

    return nomalize_pages


if __name__ == "__main__":
    select_book_index = 2 # pdf 로 변환할 책 선택

    db_path = './vFlat/bookshelf.db'
    # SQLite 데이터베이스에 연결
    with sqlite3.connect(db_path) as connection:
        # 커서 생성
        cursor = connection.cursor()

        # 테이블 목록 가져오기
        cursor.execute("SELECT id, title, cover FROM book;")
        books = cursor.fetchall()

    book = books[select_book_index]
    book_id = book[0]
    book_title = book[1]
    book_cover = book[2]

    print(book_id, book_title, book_cover)

    # SQLite 데이터베이스에 연결
    with sqlite3.connect(db_path) as connection:
        # 커서 생성
        cursor = connection.cursor()

        # 선택한 책의 페이지 가져오기
        cursor.execute(f"SELECT path, page_no FROM page WHERE path LIKE '/book_{book_id}/%';")
        vflat_pages = cursor.fetchall()

    out_pages = copy_vflat_to_out(vflat_pages, f'./out/{book_title}') # vflat page 를 page 번호 순서대로 out 폴더에 복사
    crop_pages = crop_images_by_text(out_pages, f'./out/{book_title}/crop', space = 150) # out 폴더에 있는 이미지를 텍스트 기준으로 자르기
    normalize_files = normalize_images_to_reference(crop_pages[0], crop_pages, f'./out/{book_title}/normalize') # crop 폴더에 있는 이미지를 첫번째 이미지 기준으로 정규화
    images_to_pdf(normalize_files, f'./out/{book_title}.pdf') # normalize 폴더에 있는 이미지를 PDF로 변환

    print(f"작업 완료: ./out/{book_title}.pdf")