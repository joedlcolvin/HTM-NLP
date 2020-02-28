import sqlite3
import sys
from nltk.corpus import wordnet as wn

class Similarity_Test:

    def load_sdr(self, word):
        con = sqlite3.connect('data/words_sdr.db')
        cur = con.cursor()
        cur.execute("SELECT * FROM sdrtable WHERE word=?", (word,))
        sdr = set()
        rows = cur.fetchall()
        for row in rows:
            sdr = sdr|set(int(idx) for idx in row[1].split(' '))
        return sdr

    def compute_overlap(self, word1, word2):
        sdr1 = self.load_sdr(word1)
        sdr2 = self.load_sdr(word2)
        score = len(sdr1.intersection(sdr2))
        return score

    def path_similarity(self, word1, word2):
        score = 0
        for syn1 in wn.synsets(word1):
            for syn2 in wn.synsets(word2):
                if (wn.path_similarity(syn1, syn2)):
                    score += wn.path_similarity(syn1, syn2)
        return score

if __name__ == '__main__':
    word1 = sys.argv[1]
    word2 = sys.argv[2]
    test = Similarity_Test()
    overlap = test.compute_overlap(word1, word2)
    path_sim = test.path_similarity(word1, word2)
    print(f'Overlap score: {overlap}')
    print(f'Path similarity: {path_sim}')
