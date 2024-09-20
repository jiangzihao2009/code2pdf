import os
import argparse
import shutil
import time

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--src_dir', type=str, help="project directory")
args = parser.parse_args()

input_abspath = os.path.abspath(args.src_dir)
if not os.path.exists(input_abspath):
    print(f'invalid input directory: {input_abspath}')
    exit(0)
out_dir = input_abspath + '_pdf'

def build_directory(dir_path : str):
    if os.path.exists(dir_path):
        print(f'delete old path: {dir_path}')
        shutil.rmtree(dir_path)

    try:
        os.mkdir(dir_path)
        print(f'create directory {dir_path} success')
    except:
        print(f'create directory {dir_path} failed.')

file_black_list = {'.gitignore'}
file_suffix_black_list = {}
def is_black_file(file: str):
    if file in file_black_list:
        return True
    return False

def handle_one_file(src_path: str, dst_path: str, file: str):
    filename = dst_path + '/' + file
    if is_black_file(file):
        print(f'skip file {filename}')
        return False

    src_filename = src_path + '/' + file
    dst_filename = filename + '.pdf'
    print(f'generate pdf file {dst_filename}')
    try:
        os.system(f'code2pdf -l {src_filename} {dst_filename}')
    except:
        print(f'fail, generate {dst_filename}')
        return False
    return True

def handle_one_dir(src_path: str, dst_path:str, files:list[str]):
    if not os.path.exists(dst_path):
        print(f'path: {dst_path} does not exit, fail.')
        return 0
    cnt = 0
    for file in files:
        if handle_one_file(src_path, dst_path, file):
            cnt += 1
    print(f'HANDLE {cnt}/{len(files)} files in path({dst_path})')
    return cnt

def map_absdir(path: str, src_root: str, dst_root: str):
    src_root_len = len(src_root)
    if path[:src_root_len] != src_root:
        print(f'Invalid path map, path:{path}, src root: {src_root}, dst root: {dst_root}')
        return None
    return dst_root + path[src_root_len:]

dir_black_list = {'.git'}
def is_black_path(path:str):
    base_name = os.path.basename(path)
    dir_name = os.path.dirname(path)
    if dir_name in dir_black_list or base_name in dir_black_list:
        return True
    if len(base_name) > 0 and base_name[0] == '.':
        return True
    return False

if __name__ == '__main__':
    start = time.time()
    build_directory(out_dir)
    dir_cnt = 0
    file_cnt = 0
    for path, _, files in os.walk(input_abspath):
        abs_path= os.path.abspath(path)
        if is_black_path(abs_path):
            print(f'skip path:{abs_path}')
            dir_black_list.add(abs_path)
            continue

        dir_cnt += 1
        dst_dir = out_dir
        # ignore the base root dir.
        if input_abspath != abs_path:
            dst_dir = map_absdir(abs_path, input_abspath, out_dir)
            build_directory(dst_dir)

        file_cnt += handle_one_dir(abs_path, dst_dir, files)
    print(f'create directory: {dir_cnt}, convert files: {file_cnt}')
    cost = time.time() - start
    print(f'cost time: {cost} seconds.')
