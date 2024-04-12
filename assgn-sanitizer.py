#!/usr/bin/env python3
"""Assignment Sanitizer.

This program reimplements REPOBEE's address sanitizer so that it can be run
independently.

Example:

    $ python3 assgn-sanitizer.py solution.c -o assignment.c
"""

import shutil
import re
import argparse
import sys
from pathlib import Path
from enum import Enum

# Each type of programming language has it's own line comment.
PREFIXES = {".py": "#", ".c": "//", ".cpp": "//", ".java": "//", ".fs": "//"}


def sanitize_file_lines(inpath: Path, comment_prefix: str):
    shred_pattern = re.compile(f"^[ \t]*{comment_prefix} REPOBEE-SANITIZER-SHRED")
    start_pattern = re.compile(f"^[ \t]*{comment_prefix} REPOBEE-SANITIZER-START")
    end_pattern = re.compile(f"^[ \t]*{comment_prefix} REPOBEE-SANITIZER-END")
    rpl_pattern = re.compile(f"^[ \t]*{comment_prefix} REPOBEE-SANITIZER-REPLACE-WITH")

    # The function contains a state machine, so declare the states here
    Mode = Enum("Enum", ["PASSTHROUGH", "IN_SANITIZER", "ELSE_SANITIZER"])

    lines = []
    with inpath.open() as fid:
        mode = Mode.PASSTHROUGH
        for line in fid:
            if shred_pattern.match(line):
                # This file should be skipped
                return lines
            if mode == Mode.PASSTHROUGH:
                if start_pattern.match(line):
                    mode = Mode.IN_SANITIZER
                else:
                    lines.append(line)
            elif mode == Mode.ELSE_SANITIZER:
                if end_pattern.match(line):
                    mode = Mode.PASSTHROUGH
                else:
                    idx = line.find(comment_prefix + " ")
                    before = line[0:idx]
                    after = line[idx + len(comment_prefix + " ") :]
                    lines.append(before + after)
            elif mode == Mode.IN_SANITIZER:
                if end_pattern.match(line):
                    mode = Mode.PASSTHROUGH
                elif rpl_pattern.match(line):
                    mode = Mode.ELSE_SANITIZER

        if mode == Mode.IN_SANITIZER:
            msg = "Ended with REPOBEE-SANITIZER-START but no REPOBEE-SANITIZER-END"
            raise RuntimeError(msg)
        elif mode == Mode.ELSE_SANITIZER:
            msg = (
                "Ended with REPOBEE-SANITIZER-REPLACE-WITH but no REPOBEE-SANITIZER-END"
            )
            raise RuntimeError(msg)
    return lines


def sanitize_file(inpath: Path, outpath: Path):
    """Sanitize file by discarding all lines between REPOBEE-SANITIZER-START
    and REPOBEE-SANITIZER-END, optionally replacing them with
    REPOBEE-SANITIZER-REPLACE-WITH"""

    # If the file is not a source file we can process, return the file as is
    if inpath.suffix not in PREFIXES:
        with open(inpath) as fid:
            return fid.readlines()

    # else, this has a known suffix, so let's process it
    comment_prefix = PREFIXES[inpath.suffix]

    try:
        lines = sanitize_file_lines(inpath, comment_prefix)
        if len(lines) > 0:
            with outpath.open("w") as outfile:
                for line in lines:
                    outfile.write(line)
    except RuntimeError:
        print(f"Sanitizing {inpath.name} failed")


def sanitize_directory(infile, outfile):
    if not outfile:
        msg = "Recursive mode requires outfile be provided"
        raise RuntimeError(msg)

    if not infile.exists():
        msg = f"Input path {infile} doesn't exist"
        raise OSError(msg)

    elif outfile.exists():
        msg = f"Output path {outfile} already exists!"
        raise RuntimeError(msg)

    elif outfile.exists() and not outfile.is_dir():
        msg = f"Output {outfile} is not a directory"
        raise OSError(msg)

    else:
        # First copy all files
        shutil.copytree(infile, outfile)

        # Then for each source file in the output, process and overwrite
        for f in outfile.rglob("*"):
            if f.is_file():
                sanitize_file(f, Path(f))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        "Remove solution from files of a programming assignment"
    )
    parser.add_argument("-o", "--outfile", required=True)
    parser.add_argument("infile")
    args = parser.parse_args()

    if args:
        infile = Path(args.infile)

        if not infile.exists():
            print(f"Input file {infile} doesn't exist!")
            sys.exit(1)

        elif infile.is_file():
            sanitize_file(infile, Path(args.outfile))

        elif infile.is_dir():
            sanitize_directory(infile, Path(args.outfile))

        else:
            print(f"Input file {infile} is not a file")
            sys.exit(1)
