#!/usr/bin/env python3

import shutil
import argparse
import sys
from pathlib import Path 
from enum import Enum

# Each type of programming language has it's own line comment. Declare them here.
PREFIXES = { ".py": "#", ".c": "//", ".cpp": "//", ".java": "//", ".fs": "//" }

def sanitize_file(inpath: Path):
    """Sanitize file by discarding all lines between REPOBEE-SANITIZER-START
    and REPOBEE-SANITIZER-END, optionally replacing them with
    REPOBEE-SANITIZER-REPLACE-WITH"""

    # The function contains a state machine, so declare the states here
    Mode = Enum('Enum', ['PASSTHROUGH', 'IN_SANITIZER', 'ELSE_SANITIZER'])

    # If the file is not a source file we can process, return the file as is
    if inpath.suffix not in PREFIXES:
        with open(inpath) as fid:
            return fid.readlines()

    comment_prefix = PREFIXES[inpath.suffix]

    lines = []
    with inpath.open() as fid:
        mode = Mode.PASSTHROUGH
        for line in fid:
            trimmed = line.strip()
            if mode == Mode.PASSTHROUGH:
                if trimmed.startswith(f"{comment_prefix}REPOBEE-SANITIZER-START"):
                    mode = Mode.IN_SANITIZER
                else:
                    lines.append(line)
            elif mode == Mode.ELSE_SANITIZER:
                if trimmed.startswith(f"{comment_prefix}REPOBEE-SANITIZER-END"):
                    mode = Mode.PASSTHROUGH
                else:
                    idx = line.find(comment_prefix)
                    before = line[0:idx]
                    after = line[idx+len(comment_prefix):]
                    lines.append(before+after)
            elif mode == Mode.IN_SANITIZER:
                if trimmed.startswith(f"{comment_prefix}REPOBEE-SANITIZER-END"):
                    mode = Mode.PASSTHROUGH
                elif trimmed.startswith(f"{comment_prefix}REPOBEE-SANITIZER-REPLACE-WITH"):
                    mode = Mode.ELSE_SANITIZER

        if mode == Mode.IN_SANITIZER:
            msg = "File ended with REPOBEE-SANITIZER-START but no REPOBEE-SANITIZER-END"
            raise RuntimeError(msg)
        elif mode == Mode.ELSE_SANITIZER:
            msg = "File ended with REPOBEE-SANITIZER-REPLACE-WITH but no REPOBEE-SANITIZER-END"
            raise RuntimeError(msg)
    return lines

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Remove solution from files of a programming assignment")
    parser.add_argument("-r", "--recurse", action='store_true', help="Recurse into directory")
    parser.add_argument("-o", "--outfile")
    parser.add_argument("infile")
    args = parser.parse_args()

    if args:
        if args.recurse:
            if not args.outfile:
                print(f"Recursive mode requires outfile be provided")
                sys.exit(1)

            # If recurse flag is set, assume this is a directory and 
            infile = Path(args.infile)
            outfile = Path(args.outfile)

            if not infile.exists():
                print(f"Input directory {args.infile} doesn't exist")
                sys.exit(1)
            elif not infile.is_dir():
                print(f"Input {args.infile} is not a directory")
                sys.exit(1)

            elif outfile.exists() and not args.force:
                print(f"Output directory {args.outfile} already exists!")
                sys.exit(1)
            elif outfile.exists() and not outfile.is_dir():
                print(f"Output {args.outfile} is not a directory")
                sys.exit(1)

            else:
                # First copy all files
                shutil.copytree(args.infile, args.outfile)

                # Then for each source file in the output, process and overwrite
                for f in outfile.rglob("*"):
                    if f.is_file() and f.suffix in PREFIXES:
                        lines = sanitize_file(f)
                        with f.open('w') as outfile:
                            for line in lines:
                                outfile.write(line)

        else:
            infile = Path(args.infile)
            if not infile.exists():
                print(f"Input file {args.infile} doesn't exist!")
                sys.exit(1)

            elif not infile.is_file():
                print(f"Input file {args.infile} is not a file")
                sys.exit(1)

            else:
                lines = sanitize_file(infile)
                if args.outfile:
                    # Output contents to a file
                    with open(args.outfile, 'w') as outfile:
                        for line in lines:
                            outfile.write(line)
                else:
                    # Output contents to stdout
                    for line in lines:
                        sys.stdout.write(line)

