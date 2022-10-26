#!/usr/bin/env python3

import argparse
import os
import re
import hashlib
import string
from datetime import datetime

here = os.path.abspath(os.path.dirname(__file__))
root = os.path.dirname(os.path.dirname(here))


def recursive_find(base, pattern=None):
    """
    Find filenames that match a particular pattern, and yield them.
    """
    # We can identify modules by finding module.lua
    for root, folders, files in os.walk(base):
        for file in files:
            fullpath = os.path.abspath(os.path.join(root, file))

            if pattern and not re.search(pattern, fullpath):
                continue
            yield fullpath


def write_json(json_obj, filename, mode="w"):
    """
    Write json to a filename
    """
    with open(filename, mode) as filey:
        filey.writelines(print_json(json_obj))
    return filename


def print_json(json_obj):
    """
    Print json pretty
    """
    return json.dumps(json_obj, indent=4, separators=(",", ": "))


def read_file(filename, mode="r"):
    """
    Read a file.
    """
    with open(filename, mode) as filey:
        content = filey.read()
    return content


def read_json(filename, mode="r"):
    """
    Read a json file to a dictionary.
    """
    return json.loads(read_file(filename))


def get_parser():
    parser = argparse.ArgumentParser(
        description="Split Action Parser",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("ids_file", help="Path to text file with identifiers (required).")
    parser.add_argument("--outfile", help="Output file to write to (defaults to printing to screen).")
    parser.add_argument("--calendar-split", help="Return a subset of the ids based on day of month.", action="store_true", default=False)
    parser.add_argument("--random-split", help="Randomly shuffle and split into this number", default=100, type=int)
    return parser

def random_split(lookup, N):
    """
    Given the lookup of identiiers, randomly split, and return N (default)
    """
    # 28 is minimum number of days in month we can use
    names = list(lookup)
    random.shuffle(names)
    if len(names) < N:
        N = len(names)
    return names[0:N]


def calendar_split(lookup):
    """
    Given the lookup of identiiers, split into groups equally sized
    to month days, and return today's group
    """
    # 28 is minimum number of days in month we can use
    groups = {x:set() for x in range(1, 29)}

    # Today's date 
    day = datetime.today().day
    for name in lookup:
        value = lookup[name]
                        
        # Break into 28 groups for day of month
        # We add 1 because there is no 0th day of the month
        group = int(value, base=16) % 28 + 1
        groups[group].add(name)     
    if day in groups:
        return list(groups[day])
    return []

def main():

    parser = get_parser()

    # If an error occurs while parsing the arguments, the interpreter will exit with value 2
    args, extra = parser.parse_known_args()

    # Show args to the user only if not printing to screen
    if args.outfile:
        print("             ids: %s" % args.ids_file)
        print("         outfile: %s" % args.outfile)
        print("  calendar-split: %s" % args.calendar_split)
        print("    random-split: %s" % args.random_split)

    if not os.path.exists(args.ids_file):
        sys.exit(f"{args.ids_file} does not exist.")
    lines = [x for x in read_file(args.ids_file).split('\n') if x]
    
    # Convert each to a hash
    lookup = {}
    for name in lines:
        lookup[name] = derive_hash(name) 
    
    # Case 1: calendar split breaks into 28 groups    
    if args.calendar_split:
        listing = calendar_split(lookup) 
    else:
        listing = random_split(lookup, args.random_split)
    
    result = "\n".join(listing)
    if args.outfile:
        write_file(result, args.outfile)
    else:
        print(result)
    
def derive_hash(name):
    hasher = hashlib.md5()
    hasher.update(name.encode('utf-8'))
    return hasher.hexdigest()
    
if __name__ == "__main__":
    main()
