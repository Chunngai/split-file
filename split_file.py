#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import math
import argparse
import re


def split(size, src_file, dest_dir):
    print("splitting {}".format(src_file))

    # gets the size of the pieces
    try:
        size = eval(size)
        if not type(size) == int:
            print("split_file.py: error: arg of --size should be an int")
            exit(6)
    except TypeError:
        pass

    # loads the file to be split
    with open(src_file, "rb") as f:
        file_bin_content = f.read()

    file_len = len(file_bin_content)  # length of the binary content

    # splits files
    for i in range(math.ceil(file_len / size)):
        # generates the path of a piece of file
        partial_file_path = os.path.join(dest_dir, os.path.basename(src_file).split('.')[0] + "_{}_{}".format(os.path.splitext(src_file)[-1][1:], i))

        # saves the piece
        with open(os.path.join(dest_dir, partial_file_path), "wb") as f:
            f.write(file_bin_content[:size])

            print("{} saved".format(partial_file_path))

        # gets the content of the next piece
        file_bin_content = file_bin_content[size:]

    print("done")


def combine(combined_file_name, src_path, dest_path):
    print("combining files split from {}".format(combined_file_name))

    # gets all names of files in the src dir
    file_names = os.listdir(src_path)

    # gets all pieces of the original file
    file_pieces_paths = [os.path.join(src_path, file_name) for file_name in file_names
                         if re.compile(r"{}_.*?_\d+".format(combined_file_name)).search(file_name)]
    # sorts the pieces according to the indices
    file_pieces_paths.sort(key=lambda x: int(x.split('_')[-1]))

    # checks if there are some file pieces
    if not file_pieces_paths:
        print("split_file.py: error: no file piece in {}".format(src_path))
        exit(7)

    # concatenates the pieces
    new_file_data = b''
    for i in range(len(file_pieces_paths)):
        with open(file_pieces_paths[i], "rb") as f:
            new_file_data += f.read()

    # retrieves the extension from the first piece
    combined_file_ext = file_pieces_paths[0].split("_")[-2]

    # generates the path of the combined file
    new_file_path = os.path.join(dest_path, "{}.{}".format(combined_file_name, combined_file_ext))
    # saves the file
    with open(new_file_path, "wb") as f:
        f.write(new_file_data)

    print("done")


def split_file():
    # python3 split_file.py [-s | --split]
    #                       [-f | --file FILE]
    #                       [-S | --size PIECE_SIZE]
    #                       [-c | --combine]
    #                       [-n | --name FILE_NAME]
    #                       [-h | --help]

    parser = argparse.ArgumentParser(description="split_file.py - a tool for splitting huge files into small pieces")

    parser.add_argument("--split", "-s", action="store_true", help="split a file")
    parser.add_argument("--size", "-S", action="store", default=1024 ** 2,
                        help="size of file pieces")

    parser.add_argument("--src", action="store", help="path of the file to be processed")
    parser.add_argument("--dest", action="store", default="",
                        help="path of the generated file(s) to be saved")

    parser.add_argument("--combine", "-c", action="store_true",
                        help="combine file pieces into a complete file")
    parser.add_argument("--name", "-n", action="store",
                        help="name of the complete file with or without file extension")

    args = parser.parse_args()

    if not os.path.exists(args.src):
        print("split_file.py: error: {} not exists".format(args.src))
        exit(1)
    if not os.path.exists(args.dest):
        print("split_file.py: error: {} not exists".format(args.dest))
        exit(2)

    if args.split:
        if not args.src:
            print("split_file.py: error: path of file to be split needed")
            exit(3)

        split(args.size, args.src, args.dest)
    elif args.combine:
        if not args.name:
            print("split_file.py: error: name of original file needed")
            exit(4)
        if not args.src:
            print("split_file.py: error: directory of file pieces needed")
            exit(5)

        combine(args.name, args.src, args.dest)


if __name__ == "__main__":
    split_file()
