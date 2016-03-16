__author__ = 'alenush'

import logging
from lxml import etree
import os
import pickle
from gensim.models import Word2Vec
#from find_difficult_words import Word_lists
import json


logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


LEMMAS_DIC = {}

def make_word2vec_model(sentences):
        model = Word2Vec(sentences, size=100, window=5, min_count=5, workers=4)
        model.save('./bnc_A_grammar.model')


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


def write_corpus_file(sentence):
    with open('corpus_gr.txt', 'a', encoding='utf-8') as corpus_file:
        #s_sentence = sentence.replace(" 's ", "'s ")
        corpus_file.write(sentence+'.\n')


def making_forms_dictionary(lemma, word):
    """MAking  the dictionary of all word forms"""
    if lemma not in LEMMAS_DIC.keys():
        LEMMAS_DIC[lemma] = [word]
    else:
        if word not in LEMMAS_DIC[lemma]:
            LEMMAS_DIC[lemma].append(word)

def merge_gr_sent(grammar, sentence):
    gr_sent = []
    for gr, word in zip(grammar, sentence):
        new_word = word + "_" + gr
        gr_sent.append(new_word)
    return gr_sent


def parse_BNC(path):
    """
    Go through the folders and collect sentences of
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
                        sent_gramamr = []
                        for word in sent.xpath('.//w'):
                            if word.text != None:
                                grammar = word.attrib["pos"]
                                sent_gramamr.append(grammar)
                                lemma = word.attrib['hw']
                                making_forms_dictionary(lemma, word.text.lower().rstrip(' '))
                                the_sentence.append(word.text.rstrip(' '))
                        gr_sentences = merge_gr_sent(sent_gramamr, the_sentence)
                        write_corpus_file(' '.join(gr_sentences))
                        #text_sentences.append(zip(the_sentence, sent_gramamr)) #это для грамматика + слова
    #return text_sentences# array of zip objects


def save_forms_dictionary():
    with open("dictionary_gr.json", 'w', encoding="utf-8") as out:
        json.dump(LEMMAS_DIC, out)


def convert_for_gr_model(corpus_of_sentences):
    new_corpus = []
    for sentence in corpus_of_sentences:
        sent_zips = []
        for z in sentence:
            word = z[0]+"_"+z[1]
            sent_zips.append(word)
        new_corpus.append(sent_zips)
    return new_corpus


class MySentences():
        def __iter__(self):
                for sentence in open('corpus.txt', 'r', encoding='utf-8').read().split('\n'):
                    yield sentence.split()


if __name__ == '__main__':
    path = '/home/alenush/Документы/НУГ/Texts/'
    text_sentences = parse_BNC(path)
    save_forms_dictionary()
    #print("Collect and save dictionaries. Start to convert to w2vec")
    #text_with_gr_model = convert_for_gr_model(text_sentences)
    #print("New sentences are ready")
    #make_word2vec_model(text_with_gr_model)

    #model = Word2Vec.load('./bnc_A_grammar.model')
    #variants = model.most_similar("make_VERB", topn=5)
    #print(variants)

    #text_sentences = MySentences()
    #exercise = Exercises(10)
    #exercise.excess_word_exercise()
