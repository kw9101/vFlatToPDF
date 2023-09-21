import os
import shutil
import sqlite3

if __name__ == "__main__":
    # SQLite 데이터베이스에 연결
    with sqlite3.connect('../vFlat/bookshelf.db') as connection:
        # 커서 생성
        cursor = connection.cursor()

        # 테이블 목록 가져오기
        # cursor.execute("SELECT path, page_no FROM page;")
        cursor.execute("SELECT id, title, cover FROM book;")
        books = cursor.fetchall()

    for book in books:
        book_id = book[0]
        book_title = book[1]
        book_cover = book[2]

        print(book_id, book_title, book_cover)

    # SQLite 데이터베이스에 연결
    with sqlite3.connect('../vFlat/bookshelf.db') as connection:
        # 커서 생성
        cursor = connection.cursor()

        # 테이블 목록 가져오기
        cursor.execute("SELECT path, page_no FROM page WHERE path LIKE '/book_2%';")
        pages = cursor.fetchall()

    for page in pages:
        page_path = f'.{page[0]}'

        page_no = int(page[1])

        # new_file_name = f'./out/{page_no}.jpg'
        # shutil.copy(path, new_file_name)

        print(page_path, page_no)


    # # 시작 폴더 경로
    # start_folder = './book_1'

    # # 복사 대상 폴더 경로
    # copy_to_folder = './out'  # 현재 폴더

    # # 시작 폴더에서부터 재귀적으로 자식 폴더를 찾습니다.
    # child_folders = find_child_folders(start_folder)

    # # 각 자식 폴더에 대해 파일 목록을 얻습니다.
    # all_files = []
    # for folder in child_folders:
    #     files_in_folder = get_files_in_folder(folder)
    #     all_files.extend(files_in_folder)

    # # 확장자가 없는 파일들을 필터링합니다.
    # files_with_no_extension = filter_files_with_no_extension(all_files)

    # # 확장자가 없는 파일들을 필터링하고, 작성된 순서대로 정렬합니다.
    # files_with_no_extension = sorted(filter_files_with_no_extension(all_files))

    # # 파일을 복사하고 이름을 순서대로 붙입니다.
    # for index, file_path in enumerate(files_with_no_extension, start=1):
    #     folder_name = os.path.basename(os.path.dirname(file_path))
    #     new_file_name = os.path.join(copy_to_folder, f'{index}.jpg')
    #     shutil.copy(file_path, new_file_name)

    # print("복사 및 이름 변경이 완료되었습니다.")