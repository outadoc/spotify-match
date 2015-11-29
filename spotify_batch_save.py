#!/bin/python

import spotipy
import csv
import json
import argparse

import spotipy.util as util
from itertools import izip_longest
from collections import namedtuple

Track = namedtuple("Track", "artist album track id")

def get_ids_from_matches_file():
    ids_to_save = []
    csvin = open('matches.csv')
    reader = csv.DictReader(csvin)

    for row in reader:
        track = Track(artist=row['artist'], album=row['album'], track=row['track'], id=row['id'])
        if track.id != '-1':
            ids_to_save.append(track.id)

    csvin.close()
    return ids_to_save

def group_by_n_elems(l, n):
    n = max(1, n)
    return [l[i:i + n] for i in range(0, len(l), n)]

def save_ids_to_library(sp, ids):
    ids_grp = group_by_n_elems(ids, 50)

    for group in ids_grp:
        sp.current_user_saved_tracks_add(group)

def get_args():
    # Configure the argument parser to get the user's music library path
    parser = argparse.ArgumentParser(description="Saves songs in your Spotify library from the data in a CSV file.")
    parser.add_argument('-user', metavar='username', type=str, help="your username", required=True)
    return parser.parse_args()

args = get_args()
token = util.prompt_for_user_token(args.user, "user-library-modify")

if token:
    sp = spotipy.Spotify(auth=token)

    ids = get_ids_from_matches_file()
    save_ids_to_library(sp, ids)
else:
    print "Can't get token for ", username
