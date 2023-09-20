import os
import shutil
import sqlite3

def find_child_folders(folder_path):
    child_folders = []

    # 현재 폴더에서 하위 항목(파일 및 폴더)을 모두 가져옵니다.
    items = os.listdir(folder_path)

    for item in items:
        item_path = os.path.join(folder_path, item)

        # 아이템이 폴더인 경우
        if os.path.isdir(item_path):
            child_folders.append(item_path)

            # 재귀적으로 하위 폴더를 찾습니다.
            child_folders.extend(find_child_folders(item_path))

    return child_folders

def get_files_in_folder(folder_path):
    # 폴더 내의 파일 목록을 얻습니다.
    files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    return files

def filter_files_with_no_extension(file_list):
    files_with_no_extension = []
    for file_path in file_list:
        file_name, file_extension = os.path.splitext(os.path.basename(file_path))
        if not file_extension:
            files_with_no_extension.append(file_path)
    return files_with_no_extension



if __name__ == "__main__":
    # SQLite 데이터베이스에 연결
    with sqlite3.connect('./bookshelf.db') as connection:
        # 커서 생성
        cursor = connection.cursor()

        # 테이블 목록 가져오기
        cursor.execute("SELECT path, page_no FROM page;")
        pages = cursor.fetchall()

    for page in pages:
        path = page[0]
        path = f'.{path}' # os.path.join('./', path)

        page_no = page[1]

        new_file_name = f'./{page_no}.jpg'
        shutil.copy(path, new_file_name)

        print(path)


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