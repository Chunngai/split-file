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
    with open(src_file, "rb") as f:
        file_bin_content = f.read()

    file_len = len(file_bin_content)  # length of the binary content

    # splits files
    for i in range(math.ceil(file_len / size)):
        # generates the path of a piece of file
        partial_file_path = os.path.join(dest_dir, os.path.basename(src_file) + "_{}".format(i))

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
                         if re.compile(r"{}_\d+".format(combined_file_name)).search(file_name)]
    # sorts the pieces according to the indices
    file_pieces_paths.sort(key=lambda x: int(x.split('_')[-1]))

    # checks if there are some file pieces
    if not file_pieces_paths:
        print("{}no file piece in {}".format(err_msg, src_path))
        exit(2)

    # concatenates the pieces
    new_file_data = b''
    for i in range(len(file_pieces_paths)):
        with open(file_pieces_paths[i], "rb") as f:
            new_file_data += f.read()

    # generates the path of the combined file
    new_file_path = os.path.join(dest_path, "{}".format(combined_file_name))
    # saves the file
    with open(new_file_path, "wb") as f:
        f.write(new_file_data)

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
    splitting_parser.add_argument("--split-dest", action="store", default=os.getcwd(), metavar="SPLIT_DEST",
                                  type=is_existed_dir, help="dir for storing file pieces")
    splitting_parser.set_defaults(func=lambda args: split(args.size, args.split_src, args.split_dest))

    # combines files
    combining_parser = subparsers.add_parser("combine",
                                             description="command for combining file pieces into original file",
                                             help="combine file pieces into original file")
    combining_parser.add_argument("--name", "-n", action="store", required=True, metavar="ORIGINAL_FILE_NAME",
                                  help="name of complete file with or without file extension")
    combining_parser.add_argument("--combine-src", action="store", required=True, metavar="COMBINE_SRC",
                                  type=is_existed_dir, help="dir storing needed file pieces")
    combining_parser.add_argument("--combine-dest", action="store", default=os.getcwd(), metavar="COMBINE_DEST",
                                  type=is_existed_dir, help="dir for storing generated complete file")
    combining_parser.set_defaults(func=lambda args: combine(args.name, args.combine_src, args.combine_dest))

    args = parser.parse_args()

    try:
        args.func(args)
    except AttributeError:
        pass
