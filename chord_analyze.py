#!/usr/bin/python3

import sys
import re

from pprint import pprint
from graphviz import Digraph


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
                    self.chords.append(match[1:-1])

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
        pprint(self.chain)

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

        pprint(self.chain)

    def plotModel(self, name):
        g = Digraph('G', filename = name + '.gv')

        for prevChord in self.chain:
            for chord in self.chain[prevChord]:
                g.edge(prevChord, chord, label="%.2f" % self.chain[prevChord][chord])

        g.view()

if __name__ == '__main__':
    a = Analyzer()
    a.loadChords(sys.argv[1])
    a.analyzeChords()
    a.normalizeChords()
    a.plotModel("model")
