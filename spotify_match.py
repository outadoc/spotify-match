#!/bin/python

import httplib
import urllib
import json
import argparse
import csv
import fnmatch
import os
import sys
import spotipy

from collections import namedtuple
from mutagen.easyid3 import EasyID3

sp = spotipy.Spotify()

Track = namedtuple("Track", "artist album track id")
csv_fieldnames = ['artist', 'album', 'track', 'id']

def search_for_track(title, album, artist):
    query = "track:" + title + " AND " + "artist:" + artist

    result = sp.search(q=query, limit=1, type="track")
    tracks = result['tracks']['items']

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
        update_progress(i + 1, track_count)

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

args = get_args()
generate_csv_match_report()
