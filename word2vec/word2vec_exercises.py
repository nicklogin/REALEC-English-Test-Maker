__author__ = 'alenush'

import logging
from lxml import etree
import os
import pickle
from gensim.models import Word2Vec
from find_difficult_words import Word_lists


logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


def make_word2vec_model(sentences):
        model = Word2Vec(sentences, size=100, window=5, min_count=5, workers=4)
        model.save('./bnc_A.model')


class Exercises:

    def __init__(self, number):
        self.word_list = []
        self.number_of_exercises = number
        self.name_of_exercise = ''
        self.bnc_model = Word2Vec.load('bnc.model')


    def excess_word_exercise(self):
        """
        Create exercises - which word is in excess.
        :return:
        """
        list = Word_lists()
        words = list.take_academic_wordlist()
        candidates_list = []
        for word in words:
            candidates = self.find_similar_words(word)
            if candidates != None:
                candidates_list.append((word,candidates))
                self.does_not_match(candidates)
        self.write_in_file(candidates_list)


    def find_similar_words(self, word):
        """
        Takes words from word2veca model and returns
        :return:tuple = ( word, number)
        """
        try:
            similar_words = self.bnc_model.most_similar(word, topn=4)
            return similar_words
        except:
            pass


    def does_not_match(self, candidates):
        words = []
        for cand in candidates:
            words.append(cand[0])
        print(candidates, self.bnc_model.doesnt_match(words))


    def write_in_file(self, candidates):
        with open('candidates.txt', 'w') as text:
            for cand in candidates:
                text.write(cand[0] + ' > ' )
                for four in cand[1]:
                    text.write(four[0] + '\t')
                text.write('\n')


def parse_BNC(path):
    """
    Go through the folderrs and collect sentences of
    pure corpus text for model.
    :param path: path to root folder
    :return: text_sentences - array of words
    """
    text_sentences = []
    for folders in os.listdir(path):
            for subfolders in os.listdir(path+folders):
                for files in os.listdir(path+folders+'/'+subfolders):
                    file_path = path+folders+'/'+subfolders+'/'+files
                    file_tree = etree.parse(file_path)
                    sentences = file_tree.xpath('.//s')
                    for sent in sentences:
                        the_sentence = []
                        for word in sent.xpath('.//w'):
                            if word.text != None:
                                the_sentence.append(word.text.lower())
                        text_sentences.append(the_sentence)
    return text_sentences


class MySentences():
        def __iter__(self):
                for sentence in open('corpus.txt', 'r', encoding='utf-8').read().split('\n'):
                    yield sentence.split()


if __name__ == '__main__':
    #path = '../textA/'
    #text_sentences = parse_BNC(path)
    #make_word2vec_model(text_sentences)
    #text_sentences = MySentences()
    exercise = Exercises(10)
    exercise.excess_word_exercise()
