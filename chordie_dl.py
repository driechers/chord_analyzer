#!/usr/bin/python3

import os
import random
import requests
import time

from html.parser import HTMLParser

# This parser looks for the first a href tag inside the first div of class songListContent
class SearchParser(HTMLParser):
    def initialize(self):
        self.parsing_div = False
        self.embeded_div = []
        self.song_urls = []

    def handle_starttag(self, tag, attrs):
        if tag == 'div':
            if self.parsing_div:
                self.embeded_div.append(False)
            for attr in attrs:
                if attr[0] == 'class':
                    if attr[1] == 'songListContent':
                        self.parsing_div = True
                        self.embeded_div.append(True)
                    break
        elif tag == 'a' and self.parsing_div:
            for attr in attrs:
                if attr[0] == 'href':
                    self.song_urls.append(attr[1])

    def handle_endtag(self, tag):
        if tag == 'div' and self.parsing_div:
            done_parsing_div = self.embeded_div.pop()
            if done_parsing_div:
                self.parsing_div = False

    def handle_data(self, data):
        pass

    def get_song_url(self):
        return 'https://www.chordie.com/' + self.song_urls[0]

class ChoStripper(HTMLParser):
    def initialize(self):
        self.parsing_cho = False
        self.cho_data = ''

    def handle_starttag(self, tag, attrs):
        if tag == 'textarea':
            self.parsing_cho = True

    def handle_endtag(self, tag):
        if tag == 'textarea':
            self.parsing_cho = False

    def handle_data(self, data):
        if self.parsing_cho:
            self.cho_data = data

    def write_song(self, filename):
        with open(filename, 'w') as f:
            f.write(self.cho_data)

def downloadSong(prefix, song):
    # Search for song
    parser = SearchParser()
    parser.initialize()
    search_response = requests.get('https://www.chordie.com/result.php?q=' + song.replace(' ', '+'))
    parser.feed(search_response.text)
    song_url = parser.get_song_url()
    print("Found %s" % song)

    time.sleep(random.randint(1,5))

    # Download first result
    parser = ChoStripper()
    parser.initialize()
    song_response = requests.get(song_url)
    parser.feed(song_response.text)
    parser.write_song(prefix + '/' + song.replace(' ', '_') + '.cho')
    print("Downloaded %s" % song)

    time.sleep(random.randint(1,5))

if __name__ == '__main__':
    # Download Each Song in list
    # If line starts with @ create that directory and place following files in that directory
    prefix = ''
    with open ('songlist', 'r') as f:
        for line in f.readlines():
            if line[0] == '@':
                prefix = line[1:].strip()
                if not os.path.exists(prefix):
                    os.mkdir(prefix)
            else:
                downloadSong(prefix, line.strip())
