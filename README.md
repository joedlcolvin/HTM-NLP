# HTM-NLP
This project aims to use hierarchical temporal memory (HTM) to learn the similarity of English words.

## Using python 2
1. Install, create and activate virtualenv (https://uoa-eresearch.github.io/eresearch-cookbook/recipe/2014/11/26/python-virtual-env/)
2. Ensure python 2 is installed in the envelope, and check version with pip --version
3. git pull origin master
4. pip install requirements.txt
5. ipython kernel install --name py2 --user
6. jupyter notebook
7. Go to kernel dropdown menu, select py2

## Building SDR Database
1. You must first create a folder called "data" in the project home directory.
Then, at the project home directory, run "code/SDR_builder.py". The script is compatible
with any Python version >= 2.7. The SDR database will be stored under "data/".

## Measuring SDR similarity
1. Go to the project home directory and run "python code/test_similarity.py sample_size wordnet_ic" to measure the similarity of word1 and word2.
2. Currently support SDR overlap score and WordNet path_similarity and wup_similarity, because other similarity scores cannot compare similarity between words with different POS.
3. Depending on the memory of your machine, you may want to use a small sample.
