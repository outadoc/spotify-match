#!/bin/python

import spotipy
import csv
import json

from itertools import izip_longest
from collections import namedtuple

sp = spotipy.Spotify()
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

def save_ids_to_library(ids):
    ids_grp = group_by_n_elems(ids, 50)

    for group in ids_grp:
        print json.dumps(group)

ids = get_ids_from_matches_file()
save_ids_to_library(ids)
