#!/bin/python

import httplib
import urllib
import json
import argparse
import csv
import fnmatch
import os
import sys
from itertools import izip_longest
from collections import namedtuple
from mutagen.easyid3 import EasyID3

Track = namedtuple("Track", "artist album track id")
csv_fieldnames = ['artist', 'album', 'track', 'id']

def search_for_track(title, album, artist):
    req = "/v1/search?type=track&limit=1&q="

    if title:
        req += "track%3A" + urllib.quote_plus(title) + "+"
    #if album:
    #    req += "album%3A" + urllib.quote_plus(album) + "+"
    if artist:
        req += "artist%3A" + urllib.quote_plus(artist)

    sock = httplib.HTTPSConnection('api.spotify.com')
    sock.request("GET", req)
    res = sock.getresponse()

    obj = json.loads(res.read())
    tracks = obj['tracks']['items']

    if len(tracks) > 0:
        strack = tracks[0]
        salbum = strack['album']
        sartist = strack['artists'][0]

        return Track(id=strack['id'], album=salbum['name'],
            artist=sartist['name'], track=strack['name'])

    return Track(id=-1, album=album, artist=artist, track=title)

def list_files_in_dir(dir):
    matches = []

    for root, dirnames, filenames in os.walk(dir):
        for filename in fnmatch.filter(filenames, '*.mp3'):
            matches.append(os.path.join(root, filename))

    return matches

def update_progress(curr, max):
    sys.stdout.write("\rProcessing... (" + str(curr) + "/" + str(max) + ")")

def get_args():
    # Configure the argument parser to get the user's music library path
    parser = argparse.ArgumentParser(description="Matches your local music files with their equivalent on Spotify. Make sure your ID3 tags are set properly.")
    parser.add_argument('path', metavar='library-path', type=str, help="the path to your music files")
    return parser.parse_args()

def generate_csv_match_report():
    csvout = open('matches.csv', 'wb')
    csvwriter = csv.writer(csvout)
    csvwriter.writerow(csv_fieldnames)

    track_list = list_files_in_dir(args.path)
    track_count = len(track_list)

    for i, track in enumerate(track_list):
        update_progress(i, track_count)

        # Extract ID3 tags
        audio = EasyID3(track)
        title = audio['title'][0]
        album = audio['album'][0]
        artist = audio['artist'][0]

        # Try to match and save the result in the CSV file
        match = search_for_track(title, album, artist)
        csvwriter.writerow(match)

    csvout.close()
    print "\n"

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
        sock = httplib.HTTPSConnection('api.spotify.com')
        #sock.request('PUT', '/v1/me/tracks')

args = get_args()

generate_csv_match_report()
ids = get_ids_from_matches_file()
save_ids_to_library(ids)
