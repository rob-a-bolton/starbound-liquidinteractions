#!/usr/bin/env python3

import re
import os
import shutil
import json
import argparse
from pathlib import Path
from pprint import pprint

parser = argparse.ArgumentParser(description='Processes results of mixing starbound liquids')
parser.add_argument('output', metavar='o', help='Directory to process liquid files, combining patches and removing json comments')
parser.add_argument('liquid', metavar='i', nargs='+', help='Directory containing liquid files and patch files')

args = parser.parse_args()

output_dir = Path(args.output)
liquid_dir = output_dir / "liquids"
if os.path.exists(output_dir):
    shutil.rmtree(output_dir)

os.mkdir(output_dir)
os.mkdir(liquid_dir)

input_dirs = [Path(p) for p in args.liquid]
liquidfiles_all = []

for dir in input_dirs:
    liquidfiles_all += [f for f in os.scandir(dir) if re.search(".(liquid|patch)$" , f.name)]

for f in liquidfiles_all:
    with open(f, "r") as infile:
        with open(liquid_dir / f.name, "w") as outfile:
            for line in infile:
                # Remove comments
                outfile.write(re.sub("//.*", "", line))

newfiles = [liquid_dir / f.name for f in liquidfiles_all]

# Split by liquids & patches
new_liquids = [f for f in newfiles if f.suffix == ".liquid"]
new_patches = [f for f in newfiles if f.suffix == ".patch"]

liquids = {}
for liquid_file in new_liquids:
    with open(liquid_file, "r") as l:
        liquid = json.load(l)
        liquids[liquid["name"]] = liquid

liquid_ids = {}
for name, liquid in liquids.items():
    liquid_ids[liquid["liquidId"]] = name

def process_patch(name, entry):
    # If patch is for a liquid we don't have, skip
    if not name in liquids:
        return

    liquid = liquids[name]
    if not (entry['op'] == 'add' and 'interactions' in entry['path']):
        return
    interactions = []
    if 'interactions' in liquid:
        interactions = liquid['interactions']
    interactions.append( entry['value'] )
    liquid['interactions'] = interactions

def process_patchlist(name, entries):
    for entry in entries:
        if isinstance(entry, list):
            process_patchlist(name, entry)
        else:
            process_patch(name, entry)

for patch_file in new_patches:
    liquid_name = Path(patch_file).name.split(".")[0]
    patch = None
    with open(patch_file, "r") as f:
        patch = json.load(f)
    process_patchlist(liquid_name, patch)

def has_interaction(interactions, lid):
    for entry in interactions:
        if entry['liquid'] == lid and 'liquidResult' in entry and entry['liquidResult'] != 0:
            return entry['liquidResult']

def process_interaction(liquid1, liquid2):
    id1 = liquid1['liquidId']
    id2 = liquid2['liquidId']

    interactions1 = []
    if 'interactions' in liquid1:
        interactions1 = liquid1['interactions']

    interactions2 = []
    if 'interactions' in liquid2:
        interactions2 = liquid2['interactions']

    result = has_interaction(interactions1, id2)
    if not result:
        result = has_interaction(interactions2, id1)
        
    if result:
        return result

# This stuff is gross but works
# I wanted hashmaps but lists and sets are not hashable in python,
# so we convert a list to a set, then back to a list, and to a string
# This is probably a really bad idea, but it *looks* like converting a
# set to a list always returns the items in the same order.
# If I find out this is not the case, we'll start sorting instead.
interaction_sets = {}

def pair2hash(pair):
    return " ".join(list(pair))

for liq1id, liquid1 in liquids.items():
    for liq2id, liquid2 in liquids.items():
        if liq1id == liq2id:
            next
        pair = set([liq1id, liq2id])
        result = process_interaction(liquid1, liquid2)
        if result:
            interaction_sets[pair2hash(pair)] = liquid_ids[result]

int_by_result = {}

for intpair, res in interaction_sets.items():
    inputs = []
    if res in int_by_result:
        inputs = int_by_result[res]
    inputs.append(intpair)
    int_by_result[res] = inputs

with open(output_dir / "liquids.json", "w") as f:
    json.dump(liquids, f, indent=4)

with open(output_dir / "interactions.json", "w") as f:
    json.dump(interaction_sets, f, indent=4)

with open(output_dir / "interactions-by-result.json", "w") as f:
    json.dump(int_by_result, f, indent=4)
