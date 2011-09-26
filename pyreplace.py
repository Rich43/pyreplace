#!/usr/bin/python3
import argparse
import os
import sys
import glob
import re
import shutil
from difflib import unified_diff
from os.path import join, isdir, split

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

# Define the command line arguments (see argparse docs)
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
parser.add_argument('-fd', '--filename-directory', action='store_true',
                    help='Rename directorys aswell as' + \
                         ' filenames (defaults to just filenames).')
parser.add_argument('-c', '--contents', metavar=("FIND", "REPLACE"), 
                    action='store', nargs=2,
                    help='Search contents for FIND and replace with REPLACE.')
parser.add_argument('-ci', '--contents-insensitive', action='store_true',
                    help='Ignore capital/lowercase when searching contents.')
args = parser.parse_args()

def get_file_list():
    """
    Get a list of files that will be manipulated
    """
    result = []
    # Walk the directory tree
    for root, dirs, files in os.walk(args.directory):
        # Do a glob on files in current directory
        for item in glob.glob(join(root, args.glob)):
            # Add file to list
            result.append(item)
    return result

def process_filenames():
    """
    Do find and replace on filenames from get_file_list()
    """
    # Arguments to pass into the regular expression library "re"
    opt_args = {}
    # Split filename variable
    split_f = None
    # Set insensitive flag if it is triggered on command line
    if args.filename_insensitive:
        opt_args["flags"] = re.IGNORECASE
    # Loop through files in file list
    for f in get_file_list():
        # If renaming directory's is disabled and it is a directory, ignore.
        if not args.filename_directory and isdir(f):
            continue
        # If not renaming a directory
        if not args.filename_directory:
            # Split it up, rename the filename, put back togther
            split_f = split(f)
            result = re.sub(args.filename[0], args.filename[1], 
                            split_f[1], **opt_args)
            result = join(split_f[0], result)
        else:
            # Rename everything, directory or not.
            result = re.sub(args.filename[0], args.filename[1], 
                            f, **opt_args)
        # If not a dry run, have a stab at renaming it!
        if not args.dry_run:
            shutil.move(f, result)
        # If something has changed, output the changes.
        if f != result:
            yield (f, result)

def process_contents():
    """
    Do find and replace on contents on files from get_file_list()
    """
    # Arguments to pass into the regular expression library "re"
    opt_args = {}
    # Set insensitive flag if it is triggered on command line
    if args.filename_insensitive:
        opt_args["flags"] = re.IGNORECASE
    # Loop through files in file list
    for f in get_file_list():
        # Ignore directories
        if isdir(f):
            continue
        # Attempt to read the file
        try:
            contents = str(open(f, "r").read())
        except IOError as e:
            # Cant open it for some reason, ignore.
            print(e)
            continue
        except UnicodeDecodeError:
            # Not a proper string, ignore.
            continue
        # Do a regular expression substitution.
        new_contents = re.sub(args.contents[0], args.contents[1], 
                              contents, **opt_args)
        # If its not a dry run, write the changes.
        if not args.dry_run:
            try:
                open(f, "w").write(new_contents)
            except IOError as e:
                print(e)
                continue
        # Output a diff of the changes.
        yield (f, unified_diff(contents.splitlines(1), 
                               new_contents.splitlines(1)))

def main():
    """
    Glue all the above code together
    """
    # Show help if no arguments
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    
    # Show dry run warning, if enabled.
    if args.dry_run:
        print("*" * 5 + " Dummy run, no changes will be made. " + "*" * 5)
    
    # Process filenames, use print statements if verbose or dry run
    if args.filename:
        if args.verbose or args.dry_run:
            print("Processing Filenames...")
        for result in process_filenames():
            if args.verbose or args.dry_run:
                print("Renaming %s to %s" % result)
    
    # Process contents, use print statements if verbose or dry run
    # Show a diff of changes made
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
