__author__ = 'alenush'

import pandas
import random
import itertools
from gensim.models import Word2Vec
import difflib

RIGHT_DICTIONARY = {}

with open('corpus.txt', 'r', encoding='utf-8') as source_file:
    corpus = [sentence.lower() for sentence in source_file.readlines()]


def take(n, iterable):
    """Return first n items of the iterable as a list"""
    return list(itertools.islice(iterable, n))

def random_match_exercise(number=10, write_in_file=None):
    """
    Exercise of type Match the word from right with left column
    Function takes right collocations and randomize them
    :return: rows like: coll1, coll2_wrong, coll2_right
    """
    elements = take(number, RIGHT_DICTIONARY.items())
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


    def take_context_of_sent(self, sentence):
        """ Takes +-1 sentence from out sentence"""
        sent_context = []
        try:
            my_sent_index = corpus.index(sentence.replace('#', ''))
        except:
            my_sent_index = corpus.index(sentence)
        sent_context.append(corpus[my_sent_index-1])
        sent_context.append(sentence)
        sent_context.append(corpus[my_sent_index+1])
        return sent_context


class MultipleChoice(Exercise):

    def __init__(self, whole_coll):
        super().__init__(whole_coll)


    def find_coll_in_text(self):
        """
        Find the word from collocation and takes the context.
        :return: text
        """
        for sentence in corpus:
            if self.collocation in sentence:
                new_sentence = []
                for word in sentence.split(' '):
                    if word == self.second_col:
                        new_sentence.append("#"+word+"#")
                    else:
                        new_sentence.append(word)
                return ' '.join(new_sentence) #yield

    def make_choices(self):
        """ Takes 3 candidates from word2vec"""
        model = Word2Vec.load('./word2vec/bnc.model')
        variants = model.most_similar(self.second_col, topn=5)
        choices = []
        for var in variants:
            s = difflib.SequenceMatcher(None, self.second_col, var[0])
            if s.ratio() < 0.7:
                choices.append(var[0])
        return choices[:3]


class WordFormExercise(Exercise):

    def __init__(self, whole_coll):
        super().__init__(whole_coll)


def make_multiple_choice_ex():
    with open('multiple_choice.txt', 'w', encoding='utf-8') as output:
        elements = take(5, RIGHT_DICTIONARY.items())
        for key, value in elements:
            print(key, value)
            m_ch_exer = MultipleChoice((key, value))
            sentence = m_ch_exer.find_coll_in_text()
            choices = m_ch_exer.make_choices()
            if sentence!=None:
                output.write(m_ch_exer.collocation+'\n')
                context = m_ch_exer.take_context_of_sent(sentence)
                output.write(''.join(context))
                output.write("Choices: "+','.join(choices)+'\n\n')


def wordform_exercise(number=5, write_in_file=None):
    elements = take(5, RIGHT_DICTIONARY.items())
    for key, value in elements:
        print(key, value)
        wf_ex = WordFormExercise((key, value))



def open_collocation_file():
    """Make right dictionary, where key is first component, values -- second"""
    df_collocations = pandas.read_csv('AcademicCollocationList.csv')
    begin_col = df_collocations[['Component I']]
    end_col = df_collocations[['Component II']]
    for begin, end in zip(begin_col.values, end_col.values):
        RIGHT_DICTIONARY[begin[0]] = end[0]


if __name__ == '__main__':
    open_collocation_file()
    #random_match_exercise(number=4) #write_in_file='match_exercise.txt')
    make_multiple_choice_ex()