__author__ = 'alenush'
import os
from bs4 import BeautifulSoup

""" Script clean texts and write in one new corpus file or
take categories files and clean them
"""

def bawe_file():
    with open('new_corpus.txt', 'w', encoding='utf-8') as new:

        for filename in os.listdir('../CORPUS_TXT'):
            with open('../CORPUS_TXT/' + filename) as text:
                ok_text = BeautifulSoup(text.read(), "lxml").get_text()
                sentences = ok_text.split('.')
                for sent in sentences:
                    new.write(sent+'.\n')

def categories_files():
    os.makedirs('./Categories_new/', exist_ok=True)
    for filename in os.listdir('./Categories'):
        with open('./Categories/' + filename) as text:
            ok_text = BeautifulSoup(text.read(), "lxml").get_text()
            sentences = ok_text.split('.')
            with open('./Categories_new/{}'.format(filename), 'w', encoding='utf-8') as new:
                for sent in sentences:
                    new.write(sent+'.\n')


if __name__ == '__main__':
    categories_files()