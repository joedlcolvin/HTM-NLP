import sqlite3
import sys
import random
import numpy as np
from nltk.corpus import wordnet as wn
from nltk.corpus import wordnet_ic
from nltk.corpus import genesis
from scipy import stats

# information content references
BROWN_IC = wordnet_ic.ic('ic-brown.dat')
SEMCOR_IC = wordnet_ic.ic('ic-semcor.dat')
GENESIS_IC = wn.ic(genesis, False, 0.0)

class Similarity_Test:

    def __init__(self, sample_size, ic):
        self.sample_size = sample_size
        self.ic = ic
        self.overlap = []
        self.path = []
        self.wup = []
        # Don't use the following similarity metrics because they only supports comparing words with same POS
        # self.lch = []
        # self.res = []
        # self.jcn = []
        # self.lin = []
        self._scores_over_sample()


    def _load_sdr(self, word):
        con = sqlite3.connect('data/words_sdr.db')
        cur = con.cursor()
        cur.execute("SELECT * FROM sdrtable WHERE word=?", (word,))
        sdr = set()
        rows = cur.fetchall()
        for row in rows:
            sdr = sdr|set(int(idx) for idx in row[1].split(' '))
        return sdr

    def compute_overlap(self, word1, word2):
        sdr1 = self._load_sdr(word1)
        sdr2 = self._load_sdr(word2)
        score = len(sdr1.intersection(sdr2))
        self.overlap.append(score)

    def path_similarity(self, word1, word2):
        score = 0
        for syn1 in wn.synsets(word1):
            for syn2 in wn.synsets(word2):
                if (wn.path_similarity(syn1, syn2)):
                    score += wn.path_similarity(syn1, syn2)
        self.path.append(score)

    # def lch_similarity(self, word1, word2):
    #     score = 0
    #     for syn1 in wn.synsets(word1):
    #         for syn2 in wn.synsets(word2):
    #             if (wn.lch_similarity(syn1, syn2)):
    #                 score += wn.lch_similarity(syn1, syn2)
    #     self.lch.append(score)

    def wup_similarity(self, word1, word2):
        score = 0
        for syn1 in wn.synsets(word1):
            for syn2 in wn.synsets(word2):
                if (wn.wup_similarity(syn1, syn2)):
                    score += wn.wup_similarity(syn1, syn2)
        self.wup.append(score)

    # def res_similarity(self, word1, word2):
    #     score = 0
    #     for syn1 in wn.synsets(word1):
    #         for syn2 in wn.synsets(word2):
    #             if (wn.res_similarity(syn1, syn2, self.ic)):
    #                 score += wn.res_similarity(syn1, syn2, self.ic)
    #     self.res.append(score)
    #
    # def jcn_similarity(self, word1, word2):
    #     score = 0
    #     for syn1 in wn.synsets(word1):
    #         for syn2 in wn.synsets(word2):
    #             if (wn.jcn_similarity(syn1, syn2, self.ic)):
    #                 score += wn.jcn_similarity(syn1, syn2, self.ic)
    #     self.jcn.append(score)
    #
    # def lin_similarity(self, word1, word2):
    #     score = 0
    #     for syn1 in wn.synsets(word1):
    #         for syn2 in wn.synsets(word2):
    #             if (wn.lin_similarity(syn1, syn2, self.ic)):
    #                 score += wn.lin_similarity(syn1, syn2, self.ic)
    #     self.lin.append(score)

    def concord_corr_helper(self, overlap, wn_sim):
        cor = np.corrcoef(overlap, wn_sim)[0][1]

        mean_overlap = np.mean(overlap)
        mean_wn = np.mean(wn_sim)

        var_overlap = np.var(overlap)
        var_wn = np.var(wn_sim)

        sd_overlap = np.std(overlap)
        sd_wn = np.std(wn_sim)

        numerator = 2 * cor * sd_overlap * sd_wn

        denominator = var_overlap + var_wn + (mean_overlap - mean_wn) ** 2

        return numerator / denominator

    def _scores_over_sample(self):
        words = set(wn.words())
        sample = set(random.sample(words, self.sample_size))
        for word1 in sample:
            for word2 in (sample - set([word1])):
                self.compute_overlap(word1, word2)
                self.path_similarity(word1, word2)
                # self.lch_similarity(word1, word2)
                self.wup_similarity(word1, word2)
                # self.res_similarity(word1, word2)
                # self.jcn_similarity(word1, word2)
                # self.lin_similarity(word1, word2)
                print(f"{word1} and {word2} done")
            sample = sample - set([word1])



    def calculate_corr(self, metrics):
        corr = []
        similarity = [self.path, self.wup]
        for sim in similarity:
            corr.append(metrics(self.overlap, sim))
        return corr

if __name__ == '__main__':
    sample_size = int(sys.argv[1])
    ic_name = sys.argv[2]
    ic = wordnet_ic.ic(ic_name)
    test = Similarity_Test(sample_size, ic)
    pearson = test.calculate_corr(stats.pearsonr)
    concord = test.calculate_corr(test.concord_corr_helper)

    similarity = ['path', 'wup']
    for i in range(len(similarity)):
        print(f"Pearson correlation with {similarity[i]} similarity: {pearson[i]}")
        print(f"Concordance correlation with {similarity[i]} similarity: {concord[i]}")
