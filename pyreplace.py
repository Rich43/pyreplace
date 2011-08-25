#!/usr/bin/python3
import argparse
import os
import sys
import glob
import re
from difflib import unified_diff
from os.path import join, isdir

DESCRIPTION = "Recursively find and replace in file names and contents."
EXAMPLE = """Usage Examples:
Replace foo with bar in filenames matching *.txt:
pyreplace -g *.txt -f foo bar

Find and replace foo with bar in files matching *.txt (Contents):
pyreplace -g *.txt -c foo bar

As above with all files in current directory:
pyreplace -c foo bar

As above with all files in another directory:
pyreplace -d /home/foo -c foo bar
"""

parser = argparse.ArgumentParser(description=DESCRIPTION, epilog=EXAMPLE,
                     formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument('-d', '--directory', action='store', default='.',
                    help='Set starting directory.')
parser.add_argument('-r', '--dry-run', action='store_true',
                    help='Dont make any changes, just list what would happen.')
parser.add_argument('-v', '--verbose', action='store_true',
                    help='Display changes made.')           
parser.add_argument('-g', '--glob', metavar='EXPRESSION', 
                    action='store', default="*",
                    help='Find files with matching extension. Example: *.txt')
parser.add_argument('-f', '--filename', metavar=("FIND", "REPLACE"), 
                    action='store', nargs=2,
                    help='Search filename for FIND and replace with REPLACE.')
parser.add_argument('-fi', '--filename-insensitive', action='store_true',
                    help='Ignore capital/lowercase when searching filename.')
parser.add_argument('-c', '--contents', metavar=("FIND", "REPLACE"), 
                    action='store', nargs=2,
                    help='Search contents for FIND and replace with REPLACE.')
parser.add_argument('-ci', '--contents-insensitive', action='store_true',
                    help='Ignore capital/lowercase when searching contents.')
args = parser.parse_args()

def get_file_list():
    result = []
    for root, dirs, files in os.walk(args.directory):
        for item in glob.glob(join(root, args.glob)):
            if not isdir(item):
                result.append(item)
    return result

def process_filenames():
    opt_args = {}
    if args.filename_insensitive:
        opt_args["flags"] = re.IGNORECASE
    for f in get_file_list():
        result = re.sub(args.filename[0], args.filename[1], f, **opt_args)
        if not args.dry_run:
            os.rename(f, result)
        yield (f, result)

def process_contents():
    opt_args = {}
    if args.contents_insensitive:
        opt_args["flags"] = re.IGNORECASE
    for f in get_file_list():
        try:
            contents = open(f, "r").read()
        except IOError as e:
            print(e)
            continue
        except UnicodeDecodeError:
            continue
        new_contents = re.sub(args.contents[0], args.contents[1], 
                              contents, **opt_args)
        if not args.dry_run:
            try:
                contents = open(f, "w").write(new_contents)
            except IOError as e:
                print(e)
                continue
        diff = ""
        yield (f, unified_diff(contents.splitlines(1), 
                               new_contents.splitlines(1)))

def main():
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    if args.dry_run:
        print("*" * 5 + " Dummy run, no changes will be made. " + "*" * 5)

    if args.filename:
        if args.verbose or args.dry_run:
            print("Processing Filenames...")
        for result in process_filenames():
            if args.verbose or args.dry_run:
                print("Renaming %s to %s" % result)

    if args.contents:
        if args.verbose or args.dry_run:
            print("Processing Contents...")
        for result in process_contents():
            if args.verbose or args.dry_run:
                count = 0
                for line in result[1]:
                    if count == 0:
                        print("Made following changes to %s:" % result[0])
                    print(line, end="")
                    count += 1
