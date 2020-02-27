from nltk.corpus import wordnet as wn
import sqlite3

class SDR_builder:

    # recursively get the hypernym paths of all wordnet synsets
    def get_all_synset_paths(self):
        synset_paths_dict = {}
        for synset in wn.all_synsets():
            if synset not in synset_paths_dict:
                path = synset.hypernym_paths()
                synset_paths_dict.update({synset: path})
        return synset_paths_dict

    # convert a dictionary containing all synset hypernym paths pairs
    # to a dictionary containing level-synset pairs
    # Synsets on each level are stored in set for better performance
    def paths_to_synset_structure(self, synset_paths_dict):
        synset_structure_dict = {}
        for paths in synset_paths_dict.values():  # iterate over all synsets
            # iterate over all hypernym paths of a synset
            # use enumerate() to speed up operation
            for i, path in enumerate(paths):
                for j, synset in enumerate(
                        path):  # iterate over all synsets in a hypernym path
                    key = j
                    if key not in synset_structure_dict:  # create a new level and add the synset to it
                        synset_structure_dict.update({key: {synset}})
                    # add the synset to an existing level if it isn't there yet
                    synset_structure_dict[key].add(synset)
        return synset_structure_dict

    # helper to get the entire synset structure of WordNet
    def get_all_synset_structure(self):
        synset_paths_dict = self.get_all_synset_paths()
        synset_structure_dict = self.paths_to_synset_structure(synset_paths_dict)
        return synset_structure_dict

    # build synset-index map
    def build_synset_map(self, synset_structure_dict):
        synset_structure_with_idx = {}
        for level, synsets in synset_structure_dict.items():
            indices = range(len(synsets))
            synsets_with_idx = dict(zip(synsets, indices))
            synset_structure_with_idx.update({level: synsets_with_idx})
        return synset_structure_with_idx

    # draw word from wordnet and build SDR
    def word_to_sdr(self, word, synset_structure_with_idx):
        sdr = set()
        for synset in wn.synsets(word):
            paths = synset.hypernym_paths()
            for path in paths:
                for i, hypernym in enumerate(path):
                    bit_pos = synset_structure_with_idx[i][hypernym]
                    start_idx = 0
                    curr_level = 0
                    for synsets in synset_structure_with_idx.values():
                        if curr_level < i:
                            start_idx += len(synsets)
                            curr_level += 1
                    sdr.add(start_idx + bit_pos)

            # add other lemma relations
            rel = []
            for lem in synset.lemmas():
                rel.extend(hol.synset() for hol in lem.member_holonyms())
                rel.extend(hol.synset() for hol in lem.substance_holonyms())
                rel.extend(hol.synset() for hol in lem.part_holonyms())
                rel.extend(me.synset() for me in lem.member_meronyms())
                rel.extend(me.synset() for me in lem.substance_meronyms())
                rel.extend(me.synset() for me in lem.part_meronyms())
                rel.extend(dom.synset() for dom in lem.topic_domains())
                rel.extend(dom.synset() for dom in lem.region_domains())
                rel.extend(dom.synset() for dom in lem.usage_domains())
                rel.extend(att.synset() for att in lem.attributes())
                rel.extend(der.synset() for der in lem.derivationally_related_forms())
                rel.extend(ent.synset() for ent in lem.entailments())
                rel.extend(cau.synset() for cau in lem.causes())
                rel.extend(see.synset() for see in lem.also_sees())
                rel.extend(vb.synset() for vb in lem.verb_groups())
                rel.extend(sim.synset() for sim in lem.similar_tos())
                rel.extend(per.synset() for per in lem.pertainyms())
            for related in rel:
                prev_level_len = 0
                for syns in synset_structure_with_idx.values():
                    if related in syns:
                        sdr.add(prev_level_len + syns[related])
                    prev_level_len += len(syns)
        return sdr

    # convert synset structure to SDR
    def structure_to_sdr(self, synset_structure_with_idx):
        con = sqlite3.connect("data/words_sdr.db")
        con.execute(
            "CREATE TABLE sdrtable (word, sdr)")
        sql = ''' INSERT INTO sdrtable(word, sdr)
                  VALUES(?,?) '''
        for word in wn.words():
            cursor = con.cursor()
            sdr = ' '.join(str(idx) for idx in self.word_to_sdr(word, synset_structure_with_idx))
            cursor.execute(sql, (word, sdr))
        con.commit()
        con.close()

    def build_all_sdr(self):
        synset_structure = self.get_all_synset_structure()
        synset_structure_map = self.build_synset_map(synset_structure)
        self.structure_to_sdr(synset_structure_map)

if __name__ == "__main__":
    sdr_builder = SDR_builder()
    sdr_builder.build_all_sdr()
