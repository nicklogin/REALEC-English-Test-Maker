__author__ = 'alenush'

import pandas
import random
import json
import os
from nltk import WordNetLemmatizer
from nltk.util import ngrams
import itertools
from gensim.models import Word2Vec
import difflib
from find_difficult_words import Word_lists


RIGHT_DICTIONARY = {}

with open('corpus.txt', 'r', encoding='utf-8') as source_file:
    corpus = [sentence for sentence in source_file.readlines()]


def random_match_exercise(number=10, write_in_file=None):
    """
    Exercise of type Match the word from right with left column
    Function takes right collocations and randomize them
    :return: rows like: coll1, coll2_wrong, coll2_right
    """
    elements =  random.sample(RIGHT_DICTIONARY.items(), number)
    right_col = [paar[1] for paar in elements]
    if write_in_file != None:
        with open(write_in_file, 'w', encoding='utf-8') as exercise_file:
            for key, value in elements:
                random_element = random.choice(right_col)
                exercise_file.write('{}, {}, {}\n'.format(key, random_element, value))
                right_col.remove(random_element)
    else:
        for key, value in elements:
            random_element = random.choice(right_col)
            print(key, random_element, value)
            right_col.remove(random_element)


class Exercise:

    def __init__(self, whole_coll):

        self.collocation = whole_coll[0] + ' ' + whole_coll[1]
        self.first_col = whole_coll[0]
        self.second_col = whole_coll[1]

        with open('dictionary.json', 'r', encoding="utf-8") as dictionary:
            self.lemma_dictionary = json.load(dictionary)


    def take_context_of_sent(self, sentence):
        """ Takes +-1 sentence from out sentence"""
        sent_context = []
        try:
            my_sent_index = corpus.index(sentence.replace('#', ''))
        except:
            my_sent_index = corpus.index(sentence)
        if len(corpus[my_sent_index-1]) > 3 and len(corpus[my_sent_index+1]) > 3:
            sent_context.append(corpus[my_sent_index-1])
            sent_context.append(sentence)
            sent_context.append(corpus[my_sent_index+1])
            return sent_context

    def find_coll_in_text(self, collocate_part=1):
        """
        Find the word from collocation
        :collocate_part: 1 or 0, 0 -is first part, 1 is second
        :return: text
        """
        for sentence in corpus:
            sent_coll = self.check_whole_collocation(sentence)
            if sent_coll!= False:
                new_sentence = []
                for word in sentence.split(' '):
                    if word == sent_coll[collocate_part]:
                        new_sentence.append("#"+word+"#")
                    else:
                        new_sentence.append(word)
                return ' '.join(new_sentence)


    def check_whole_collocation(self, sentence):
        """
        Generate part1 + part2 possible variants
        :param col
        """
        collocate_set = set()
        lmtzr = WordNetLemmatizer()
        lemmas1 = lmtzr.lemmatize(self.first_col)
        lemmas2 = lmtzr.lemmatize(self.second_col)
        for lem1 in self.lemma_dictionary[lemmas1]:
            for lem2 in self.lemma_dictionary[lemmas2]:
                collocate_set.add((lem1, lem2))
        for col in collocate_set:
            my_col = col[0]+" "+col[1]
            if my_col in sentence:
                return col
        return False

class MultipleChoice(Exercise):

    def __init__(self, whole_coll):
        super().__init__(whole_coll)

    def make_choices(self):
        """ Takes 3 candidates from word2vec"""
        model = Word2Vec.load('./word2vec/bnc.model')
        variants = model.most_similar(self.second_col, topn=7)
        choices = []
        for var in variants:
            s = difflib.SequenceMatcher(None, self.second_col, var[0])
            if s.ratio() < 0.7:
                choices.append(var[0])
            else:
                continue
        return choices[:3]


class OpenCloze(Exercise):

    def __init__(self, whole_coll):
        super().__init__(whole_coll)

    def find_collocation(self, number):
        """
        Find whol collocation. make gap from it and safe collocate as a write answer.
        :return: sentence and tuple = (col1, col2)
        """
        for sentence in corpus:
            if self.collocation in sentence:
                bigrams = ngrams(sentence.split(' '), 2)
                for big in bigrams:
                    if big[0] in self.first_col and big[1] in self.second_col:
                        sent_first = sentence.split(' ')[:sentence.split(' ').index(big[0])]
                        sent_second = sentence.split(' ')[sentence.split(' ').index(big[1])+1:]
                        sentence = "{} #{}# {}".format(' '.join(sent_first), number, ' '.join(sent_second))
                        print(sentence, big)
                        return sentence, big

def write_in_file(file_name, data):
    with open(file_name, 'w', encoding='utf-8') as filewrite:
        for row in data:
            filewrite.write(row[0])
            filewrite.write(row[1][0]+" "+row[1][1]+'\n\n')


class WordFormExercise(Exercise):

    def __init__(self, whole_coll):
        super().__init__(whole_coll)

    def word_form_variance(self, wf_dictionary):
        """
        :return:sentence with gap and two words: right form and headword
        """
        for key, value in wf_dictionary.items():
            if self.first_col in value:
                print("HEADWORD: ", key)
            elif self.second_col in value:
                print("HEADWORD: ", key)



def make_multiple_choice_ex(number_inside=5, number_of_files=1):
    """
    Function for calling and writing multiple choice exercises
    :param number_inside: number of exercises inside one document
    :param number_of_files: number of documentts
    """
    os.makedirs('./multiple_choice_exercises', exist_ok=True)
    for i in range(0,number_of_files):
        with open('./multiple_choice_exercises/multiple_choice{}.txt'.format(i), 'w', encoding='utf-8') as output:
            elements =  random.sample(RIGHT_DICTIONARY.items(), number_inside)
            for key, value in elements:
                print(key, value)
                m_ch_exer = MultipleChoice((key, value))
                sentence = m_ch_exer.find_coll_in_text(1)
                choices = m_ch_exer.make_choices()
                if sentence != None:
                    output.write(m_ch_exer.collocation+'\n')
                    context = m_ch_exer.take_context_of_sent(sentence)
                    output.write(''.join(context))
                    output.write("Choices: "+','.join(choices)+'\n\n')


def wordform_exercise(number=5):
    elements =  random.sample(RIGHT_DICTIONARY.items(), number)
    wf = Word_lists()
    wf.takes_wordforms()
    wf_dictionary = wf.wordform_dictionary
    for key, value in elements:
        print(key, value)
        wf_ex = WordFormExercise((key, value))
        wf_ex.find_coll_in_text(1)
        wf_ex.word_form_variance(wf_dictionary)


def open_cloze_exersize(number=5, file_name=None):
    elements =  random.sample(RIGHT_DICTIONARY.items(), number)
    data = []
    for n, paar in enumerate(elements):
        print(n, paar[0], paar[1])
        op_ex = OpenCloze((paar[0], paar[1]))
        try:
            sentence, collocate = op_ex.find_collocation(n)
            data.append((sentence, collocate))
        except:
            print("No sentence with collocation")
    write_in_file(file_name, data)


def open_collocation_file():
    """Make right dictionary, where key is first component, values -- second"""
    df_collocations = pandas.read_csv('AcademicCollocationList.csv')
    begin_col = df_collocations[['Component I']]
    end_col = df_collocations[['Component II']]
    for begin, end in zip(begin_col.values, end_col.values):
        if '(' not in begin[0] and '(' not in end[0]:
            RIGHT_DICTIONARY[begin[0]] = end[0]


if __name__ == '__main__':
    open_collocation_file()
    #random_match_exercise(number=5, write_in_file='match_exercise.txt') #ok
    make_multiple_choice_ex(number_inside=3, number_of_files=10)
    #wordform_exercise(number=5)
    #open_cloze_exersize(number=5, file_name='open_cloze.txt')
    #word bank доделать норально. Или из опен-клоз создать