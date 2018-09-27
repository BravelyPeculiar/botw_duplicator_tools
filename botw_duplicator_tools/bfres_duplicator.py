import os
import argparse

import wszst_yaz0

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("old_file_path", help="The path of the bfres/bitemico file you want to duplicate")
    parser.add_argument("new_file_path", help="The path for the duplicated bfres/bitemico - its name must be the same length as the original name")

    args = parser.parse_args()

    ###

    old_bfres_name = os.path.basename(args.old_file_path).split(".")[0]
    new_bfres_name = os.path.basename(args.new_file_path).split(".")[0]

    if not os.path.isfile(args.old_file_path):
        print("'" + args.old_file_path +"' does not exist")
        exit()
    if os.path.isfile(args.new_file_path):
        print("'" + args.new_file_path +"' already exists")
        exit()
    if len(old_bfres_name) != len(new_bfres_name):
        print("'" + old_bfres_name + "' --> '" + new_bfres_name + "' - New name must be same length as old name")
        exit()

    is_yaz0 = False
    with open(args.old_file_path, "rb") as file:
        bfres_rawdata = file.read()
    if bfres_rawdata[:4] == b"Yaz0":
        bfres_rawdata = wszst_yaz0.decompress(bfres_rawdata)
        is_yaz0 = True

    bfres_rawdata = bfres_rawdata.replace(old_bfres_name.encode(), new_bfres_name.encode())

    if is_yaz0:
        bfres_rawdata = wszst_yaz0.compress(bfres_rawdata, level=10)
    with open(args.new_file_path, "wb") as file:
        file.write(bfres_rawdata)

if __name__ == '__main__':
    main()