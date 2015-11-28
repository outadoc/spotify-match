#!/bin/python

import httplib
import urllib
import json
import argparse
import csv

import fnmatch
import os
from collections import namedtuple
from mutagen.easyid3 import EasyID3

Track = namedtuple("Track", "id track album artist")

def search_for_track(title, album, artist):
    req = "/v1/search?type=track&limit=1&q="

    if title:
        req += "track%3A" + urllib.quote_plus(title) + "+"
    if album:
        req += "album%3A" + urllib.quote_plus(album) + "+"
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

# Configure the argument parser to get the user's music library path
parser = argparse.ArgumentParser(description='Matches your local music files with their equivalent on Spotify. Make sure your ID3 tags are set properly.')
parser.add_argument('path', metavar='library-path', type=str, help='the path to your music files')
args = parser.parse_args()

csvout = open('matches.csv', 'w')
csvwriter = csv.writer(csvout)

for track in list_files_in_dir(args.path):
    audio = EasyID3(track)

    title = audio["title"][0]
    album = audio["album"][0]
    artist = audio["artist"][0]

    match = search_for_track(title, album, artist)
    csvwriter.writerow(match)
    print match
