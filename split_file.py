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
        size = eval(str(size))
        if not type(size) == int:
            raise
    except:
        print("{}arg of --size should be an int".format(err_msg))
        exit(1)

    # loads the file to be split
    with open(src_file, "rb") as f_read:
        count = 0
        while True:
            file_partial_bin_content = f_read.read(size)

            if not file_partial_bin_content:
                break

            # generates the path of the file piece
            partial_file_path = os.path.join(dest_dir, os.path.basename(src_file) + "_{}".format(count))

            # saves the piece
            with open(os.path.join(dest_dir, partial_file_path), "wb") as f_write:
                f_write.write(file_partial_bin_content)

                print("{} saved".format(partial_file_path))

            count += 1

    print("done")


def _process_combined_file_name(combined_file_name):
    meta_chr_str = ".^$*+?{}[]\\|()"

    i = 0
    name_len = len(combined_file_name)
    while i < name_len:
        if combined_file_name[i] in meta_chr_str:
            combined_file_name = f"{combined_file_name[:i]}\\{combined_file_name[i:]}"
            i += 1
            name_len += 1

        i += 1

    return combined_file_name


def combine(combined_file_name, src_path, dest_path):
    print("combining files split from {}".format(combined_file_name))

    # inserts a '\' before meta characters of re
    combined_file_name_processed = _process_combined_file_name(combined_file_name)

    # gets all names of files in the src dir
    file_names = os.listdir(src_path)

    # gets all pieces of the original file
    file_pieces_paths = [os.path.join(src_path, file_name) for file_name in file_names
                         if re.compile(r"{}_\d+".format(combined_file_name_processed)).search(file_name)]
    # sorts the pieces according to the indices
    file_pieces_paths.sort(key=lambda x: int(x.split('_')[-1]))

    # checks if there are some file pieces
    if not file_pieces_paths:
        print("{}no file piece in {}".format(err_msg, src_path))
        exit(2)

    # generates the path of the combined file
    new_file_path = os.path.join(dest_path, "{}".format(combined_file_name))

    # concatenates the file
    with open(new_file_path, "ab") as f_append:
        for i in range(len(file_pieces_paths)):
            with open(file_pieces_paths[i], "rb") as f_read:
                f_append.write(f_read.read())

    # deletes file pieces
    for i in range(len(file_pieces_paths)):
        os.remove(file_pieces_paths[i])

    print("done")


def is_existed_file(input_path):
    if not os.path.exists(input_path):
        raise argparse.ArgumentTypeError("file not exists")
    if not os.path.isfile(input_path):
        raise argparse.ArgumentTypeError("not a file")

    return input_path


def is_existed_dir(input_path):
    if not os.path.exists(input_path):
        raise argparse.ArgumentTypeError("dir not exists")
    if not os.path.isdir(input_path):
        raise argparse.ArgumentTypeError("not a dir")

    return input_path


if __name__ == "__main__":
    err_msg = "split_file.py: error: "

    parser = argparse.ArgumentParser(description="split_file.py - a tool for splitting huge files into small pieces")
    subparsers = parser.add_subparsers(title="sub commands", help="valid sub commands")

    # splits files
    splitting_parser = subparsers.add_parser("split", description="command for splitting huge files",
                                             help="split a file")
    splitting_parser.add_argument("--size", "-s", action="store", default=pow(2, 20), metavar="FILE_PIECE_SIZE",
                                  help="size of file pieces")
    splitting_parser.add_argument("--split-src", action="store", required=True, metavar="SPLIT_SRC",
                                  type=is_existed_file, help="file to be split")
    splitting_parser.add_argument("--split-dest", action="store", metavar="SPLIT_DEST",
                                  type=is_existed_dir, help="dir for storing file pieces")
    splitting_parser.set_defaults(func=lambda args: split(args.size, args.split_src, args.split_dest))

    # combines files
    combining_parser = subparsers.add_parser("combine",
                                             description="command for combining file pieces into original file",
                                             help="combine file pieces into original file")
    combining_parser.add_argument("--name", "-n", action="store", required=True, metavar="ORIGINAL_FILE_NAME",
                                  help="name of the original file with file extension")
    combining_parser.add_argument("--combine-src", action="store", required=True, metavar="COMBINE_SRC",
                                  type=is_existed_dir, help="dir storing needed file pieces")
    combining_parser.add_argument("--combine-dest", action="store", metavar="COMBINE_DEST",
                                  type=is_existed_dir, help="dir for storing generated complete file")
    combining_parser.set_defaults(func=lambda args: combine(args.name, args.combine_src, args.combine_dest))

    args = parser.parse_args()

    try:
        if "split_src" in list(vars(args).keys()) and args.split_dest is None:
            args.split_dest = os.path.split(args.split_src)[0]

        if "combine_src" in list(vars(args).keys()) and args.combine_dest is None:
            args.combine_dest = args.combine_src

        args.func(args)
    except AttributeError:
        pass
