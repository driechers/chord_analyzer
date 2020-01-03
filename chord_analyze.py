#!/usr/bin/python3

import operator
import sys
import re

from pprint import pprint
from graphviz import Digraph

# Can a chord be minor sus or minor aug? how is partially diminished written in chord pro?
chordRE = "^([A-G][#b]{0,1})(maj|m|dim|aug){0,1}([0-9]*)(sus){0,1}([0-9]*)$"

class Analyzer:
    def __init__(self):
        self.chords = []
        # Key is source chord value is dict key dst chord value percentage
        self.chain = {}

    def loadChords(self, choFile):
        """
        This method loads chord pro files and extracts just the chords in the
        order they are played.
        """
        self.chords = []
        with open(choFile, 'r') as f:
            for line in f:
                for match in re.findall("\[.*?\]", line):
                    chord = match[1:-1]
                    if re.search(chordRE, chord) is not None:
                        self.chords.append(chord)
                    else:
                        print(chord + " is not a chord")

    def __getCounterClock(self, chord):
        """
        This method get the chord one counter clockwise on the circle of fifths
        Gb always turns into F#
        """
        lookupTable = {
                'C': 'F', 'Am': 'Dm', 'G': 'C', 'Em': 'Am', 'D': 'G',
                'Bm': 'Em', 'A': 'D', 'F#m': 'Bm', 'E': 'A', 'C#m': 'F#m' ,
                'B': 'E', 'G#m': 'C#m', 'F#': 'B', 'Gb': 'B', 'Ebm': 'G#m',
                'Db': 'F#', 'Bbm': 'Ebm', 'Ab': 'Db', 'Fm': 'Bbm', 'Eb': 'Ab',
                'Cm': 'Fm', 'Bb': 'Eb', 'Gm': 'Cm', 'F': 'Bb', 'Dm': 'Gm'
                }

        return lookupTable[chord]

    def __getSupportingChords(self, key):
        """
        This method gets the legal supporting chords for the given key based on the circle of fifths
        """
        lookupTable = {
                'C': ('F', 'Dm', 'C', 'Am', 'G', 'Em'),
                'Am': ('F', 'Dm', 'C', 'Am', 'G', 'Em'),

                'G': ('C', 'Am', 'G', 'Em', 'D', 'Bm'),
                'Em': ('C', 'Am', 'G', 'Em', 'D', 'Bm'),

                'D': ('G', 'Em', 'D', 'Bm', 'A', 'F#m'),
                'Bm': ('G', 'Em', 'D', 'Bm', 'A', 'F#m'),

                'A': ('D', 'Bm', 'A', 'F#m', 'E', 'C#m'),
                'F#m': ('D', 'Bm', 'A', 'F#m', 'E', 'C#m'),

                'E': ('A', 'F#m', 'E', 'C#m', 'B', 'G#m'),
                'C#m': ('A', 'F#m', 'E', 'C#m', 'B', 'G#m'),

                'B': ('E', 'C#m', 'B', 'G#m', 'F#', 'Gb', 'Ebm'),
                'G#m': ('E', 'C#m', 'B', 'G#m', 'F#', 'Gb', 'Ebm'),

                'F#': ('B', 'G#m', 'F#', 'Gb', 'Ebm', 'Db', 'Bbm'),
                'Gb#': ('B', 'G#m', 'F#', 'Gb', 'Ebm', 'Db', 'Bbm'),
                'Ebm': ('B', 'G#m', 'F#', 'Gb', 'Ebm', 'Db', 'Bbm'),

                'Db': ('F#', 'Gb', 'Eb', 'Db', 'Bbm', 'Ab', 'Fm'),
                'Bbm': ('F#', 'Gb', 'Eb', 'Db', 'Bbm', 'Ab', 'Fm'),

                'Ab': ('Db', 'Bbm', 'Ab', 'Fm', 'Eb', 'Cm'),
                'Fm': ('Db', 'Bbm', 'Ab', 'Fm', 'Eb', 'Cm'),

                'Eb': ('Ab', 'Fm', 'Eb', 'Cm', 'Bb', 'Gm'),
                'Cm': ('Ab', 'Fm', 'Eb', 'Cm', 'Bb', 'Gm'),

                'Bb': ('Eb', 'Cm', 'Bb', 'Gm', 'F', 'Dm'),
                'Gm': ('Eb', 'Cm', 'Bb', 'Gm', 'F', 'Dm'),

                'F': ('Bb', 'Gm', 'F', 'Dm', 'C', 'Am'),
                'Dm': ('Bb', 'Gm', 'F', 'Dm', 'C', 'Am')
                }

    def getKey(self):
        """
        This method determines the key of the chord progression. It works using the following
        methods and weighted voting.

        Method                                Weight
        --------------------------------------------
        First Chord                           1
        Last Chord                            1
        First and Last Matching tie breaker   1
        Dominant Seventh                      1
        Circle of Fifths                      1
        """

        votes = {
                'C': 0, 'Am': 0, 'G': 0, 'Em': 0, 'D': 0,
                'Bm': 0, 'A': 0, 'F#m': 0, 'E': 0, 'C#m': 0,
                'B': 0, 'G#m': 0, 'F#': 0, 'Gb': 0, 'Ebm': 0,
                'Db': 0, 'Bbm': 0, 'Ab': 0, 'Fm': 0, 'Eb': 0,
                'Cm': 0, 'Bb': 0, 'Gm': 0, 'F': 0, 'Dm': 0
                }

        histogram = {
                'C': 0, 'Am': 0, 'G': 0, 'Em': 0, 'D': 0,
                'Bm': 0, 'A': 0, 'F#m': 0, 'E': 0, 'C#m': 0,
                'B': 0, 'G#m': 0, 'F#': 0, 'Gb': 0, 'Ebm': 0,
                'Db': 0, 'Bbm': 0, 'Ab': 0, 'Fm': 0, 'Eb': 0,
                'Cm': 0, 'Bb': 0, 'Gm': 0, 'F': 0, 'Dm': 0
                }
        # TODO combine Gb and F# votes

        strippedChords = []
        prevParts = None
        for chord in self.chords:
            parts = re.search(chordRE, chord).groups()
            if parts[1] == None:
                strippedChords.append(parts[0])
                histogram[parts[0]] += 1
            if parts[1] == 'maj':
                strippedChords.append(parts[0])
                histogram[parts[0]] += 1
            if parts[3] == 'sus':
                strippedChords.append(parts[0])
                histogram[parts[0]] += 1
            if parts[1] == 'm':
                strippedChords.append(parts[0] + parts[1])
                histogram[parts[0] + parts[1]] += 1

            # Look for Dominant 7 chords
            if parts[1] == None and parts[2] == '7':
                # Cast vote for key one clockwise on circle of fifths
                # TODO should this really get a vote for each instance of a chord?
                votes[self.__getCounterClock(parts[0])] += 1

            # Look for resolutions TODO: add check for V -> I
            if prevParts is not None:
                # Previous Chord is dissonant ( dim, sus, or extended )
                # TODO: are aug chords dissonant?
                if prevParts[1] == 'dim' or prevParts[3] == 'sus' or len(prevParts[2]) > 0:
                    # Current Chord is consonant ( not dim, special, sus, or extended)
                    if parts[1] == '' and parts[3] == '' or len(parts[2]) == 0:
                        # Cast vote for consonent chord
                        votes[chord] += 1

            prevParts = parts

        # Cast vote for first note
        votes[strippedChords[0]] += 1
        # Cast vote for last note
        votes[strippedChords[-1]] += 1
        # Cast extra vote if they match
        if strippedChords[0] == strippedChords[-1]:
            votes[strippedChords[0]] += 1


        # TODO cast vote for circle of fifths method

        sortedHistogram = sorted(histogram.items(), key=operator.itemgetter(1), reverse=True)
        #print(sortedHistogram)

        #print(self.chords)
        pprint(votes)
        print(max(votes.items(), key=operator.itemgetter(1))[0])
        return max(votes.items(), key=operator.itemgetter(1))[0]

    def analyzeChords(self):
        """
        This method creates a markovian chain of the chords but does not
        normalize the edges. This method can be called several times to create
        a chain spanning several songs.
        """
        prevChord = None

        for chord in self.chords:
            if prevChord is not None:
                if prevChord in self.chain:
                    if chord in self.chain[prevChord]:
                        # chord exists count it
                        self.chain[prevChord][chord] += 1.
                    else:
                        # chord not yet in chain as dest add it
                        self.chain[prevChord][chord] = 1.
                else:
                    # chord not yet in chain add it and dest chord
                    self.chain[prevChord] = {}
                    self.chain[prevChord][chord] = 1.

            prevChord = chord
        #pprint(self.chain)

    def normalizeChords(self):
        """
        This method takes chords that have been analyzed and normalizes them
        Once normalized they are percentages rather than counts.
        """
        for prevChord in self.chain:
            #print("%s: %d" % (prevChord, len(self.chain[prevChord])))
            total = 0.
            for chord in self.chain[prevChord]:
                total += self.chain[prevChord][chord]
            for chord in self.chain[prevChord]:
                self.chain[prevChord][chord] /= total

        #pprint(self.chain)

    def plotModel(self, name):
        """
        This method plots the markov chain with graphviz and displays it and saves
        it as a gv file and a pdf file.
        """
        g = Digraph('G', filename = name + '.gv')

        for prevChord in self.chain:
            for chord in self.chain[prevChord]:
                g.edge(prevChord, chord, label="%.2f" % self.chain[prevChord][chord])

        g.view()

if __name__ == '__main__':
    a = Analyzer()
    a.loadChords(sys.argv[1])
    a.getKey()
    a.analyzeChords()
    a.normalizeChords()
    a.plotModel("model")
