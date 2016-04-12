__author__ = 'alenush'

import pandas
import random
import json
import os
from nltk import WordNetLemmatizer
from nltk import word_tokenize
from gensim.models import Word2Vec
import difflib


RIGHT_DICTIONARY = {}

with open('new_corpus.txt', 'r', encoding='utf-8') as source_file:
    corpus = [sentence for sentence in source_file.readlines()]


def random_match_exercise(number=5, number_of_files=5):
    """
    Exercise of type Match the word from right with left column
    Function takes right collocations and randomize them
    :return: rows like: coll1, coll2_wrong, coll2_right
    """
    os.makedirs('./match_exercises', exist_ok=True)
    for i in range(0, number_of_files):
        with open('./match_exercises/match_exercises{}.txt'.format(i), 'w', encoding='utf-8') as output:
            elements = random.sample(RIGHT_DICTIONARY.items(), number)
            right_col = [paar[1] for paar in elements]
            for key, value in elements:
                print(key,value)
                random_element = random.choice(right_col)
                output.write('{}, {}, {}\n'.format(key, random_element, value))
                right_col.remove(random_element)

class Exercise:

    def __init__(self, whole_coll):

        self.collocation = whole_coll[0] + ' ' + whole_coll[1]
        self.first_col = whole_coll[0]
        self.second_col = whole_coll[1]

        with open('dictionary.json', 'r', encoding="utf-8") as dictionary:
            self.lemma_dictionary = json.load(dictionary)

    def take_context_of_sent(self, sentence):
    #:todo make function that revert to punction standarts! # and add it before looking for context
        """ Takes +-1 sentence from out sentence"""
        sent_context = []
        try:
            my_sent_index = corpus.index(sentence)
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
            sent_coll = self.check_whole_collocation(sentence) #check all possible variants
            if sent_coll!= False:
                new_sentence = []
                for word in word_tokenize(sentence):
                    if word == sent_coll[collocate_part]:
                        new_sentence.append("______")
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
        try:
            for lem1 in self.lemma_dictionary[lemmas1]:
                for lem2 in self.lemma_dictionary[lemmas2]:
                    collocate_set.add((lem1, lem2))
        except:
            collocate_set.add((lemmas1, lemmas2))
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
                choices.append(var[0].lower())
            else:
                continue
        return choices[:3]

    def write_in_normal_format(self, sentence, choices, output):
        """
        Write everything in txt file. Sentence with #answer# and Choices:...
        :param sentence:
        :param choices:
        :param output: io object
        """
        output.write(self.collocation+'\n')
        #context = self.take_context_of_sent(sentence)
        #if context:
        output.write(''.join(sentence)+'\n')
        output.write("Choices: "+','.join(choices)+'\n\n')

    @staticmethod
    def write_in_moodle_xml(number, data_array, io_object, name="multichoice"):
            """
            :param data_array: array of one exercise
            For M_ch: sentence, array of choices, answer
            :param name: type of exercise; ex: multichoice
            :param io_object: with open() as io_object
            Writes one question in file in moodle format
            """
            io_object.write('<question type="{}">\n'.format(name))
            io_object.write('<name><text>Question {}</text></name>\n'.format(number))
            io_object.write('<questiontext format="html">\n<text><![CDATA[<p>'
                            '{}<br></p>]]></text>\n</questiontext>\n'.format(data_array[0]))
            io_object.write("<defaultgrade>1.0000000</defaultgrade>\n<penalty>0.3333333</penalty>\n"
                            "<hidden>0</hidden>\n<single>true</single>\n<shuffleanswers>true</shuffleanswers>\n"
                            "<answernumbering>abc</answernumbering>\n<correctfeedback format='html'>\n"
                            "<text>Your answer is correct.</text>\n</correctfeedback>\n"
                            "<partiallycorrectfeedback format='html'>\n<text>Your answer is partially correct.</text>\n"
                            "</partiallycorrectfeedback>\n<incorrectfeedback format='html'>\n"
                            "<text>Your answer is incorrect.</text>\n</incorrectfeedback>\n")
            for answer in data_array[1]:
                correct = 0
                if answer == data_array[2]:
                    correct = 100
                io_object.write('<answer fraction="{}" format="html">\n<text><![CDATA[<p>{}<br></p>]]>'
                                '</text>\n<feedback format="html">\n</feedback>\n</answer>\n'.format(correct, answer))
            io_object.write('</question>\n')



class OpenCloze(Exercise):

    def __init__(self, whole_coll):
        super().__init__(whole_coll)

    def find_collocation(self, number):
        """
        Find whole collocation. make gap from it and safe collocate as a write answer.
        :return: sentence and tuple = (col1, col2)
        """
        # for sentence in corpus:
        #     if self.collocation in sentence:
        #         bigrams = ngrams(sentence.split(' '), 2)
        #         for big in bigrams:
        #             if big[0] in self.first_col and big[1] in self.second_col:#тут поменять условие!
        #                 sent_first = sentence.split(' ')[:sentence.split(' ').index(big[0])]
        #                 sent_second = sentence.split(' ')[sentence.split(' ').index(big[1])+1:]
        #                 sentence = "{} #{}# {}".format(' '.join(sent_first), number, ' '.join(sent_second))
        #                 print(sentence, big)
        #                 return sentence, big
        for sentence in corpus:
            col = self.check_whole_collocation(sentence)
            if col != False:
                split_sent = sentence.split(' ')
                print(split_sent)
                print(col[0], col[1])
                sent_first = split_sent[:split_sent.index(split_sent[0])]
                sent_second = split_sent[split_sent.index(split_sent[1])+1:]
                sentence = "{} #{}# {}".format(' '.join(sent_first), number, ' '.join(sent_second))
                print(sentence, col)
                return sentence, col


class WordFormExercise(Exercise):

    def __init__(self, whole_coll):
        super().__init__(whole_coll)

        with open('wordforms.json', 'r', encoding="utf-8") as dictionary:
            self.wf_dictionary = json.load(dictionary) #{'headword':[words,words,words]}

    def word_form_variance(self, wf_dictionary):
        """
        :return:sentence with gap and two words: right form and headword
        """
        for key, value in wf_dictionary.items():
            if self.first_col in value:
                print("HEADWORD: ", key)
            elif self.second_col in value:
                print("HEADWORD: ", key)

    def check_headword(self, my_col):
        """Return headword from the dictionary"""
        for key, value in self.wf_dictionary.items():
            headword = [val for val in value if val == my_col]
            if len(headword)>0:
                return key



def wordform_exercise(number=5, number_of_files=5):
    os.makedirs('./wordforms_exercises', exist_ok=True)
    for i in range(0,number_of_files):
        with open('./wordforms_exercises/wordform{}.txt'.format(i), 'w', encoding='utf-8') as output:
            elements =  random.sample(RIGHT_DICTIONARY.items(), number)
            for key, value in elements:
                print(key, value)
                wf_ex = WordFormExercise((key, value))
                headword = wf_ex.check_headword(key)
                if headword!=None:
                    sentence = wf_ex.find_coll_in_text(0)
                    if sentence != None:
                        output.write(sentence+'\n')
                        output.write(headword+'\n\n')


def open_cloze_exercise(number=5, number_of_files=5):
    """Make open cloze execises and write in files"""
    os.makedirs('./open_cloze_exercises', exist_ok=True)
    for i in range(0, number_of_files):
        with open('./open_cloze_exercises/open_cloze{}.txt'.format(i), 'w', encoding='utf-8') as output:
            elements = random.sample(RIGHT_DICTIONARY.items(), number)
            data = []
            for n, paar in enumerate(elements):
                print(n, paar[0], paar[1])
                op_ex = OpenCloze((paar[0], paar[1]))
                try:
                    sentence, collocate = op_ex.find_collocation(n) #TODO: not all forms are checked
                    data.append((sentence, collocate))
                except:
                    print("No sentence with collocation")
                    n += 1
            for row in data:
                output.write(row[0])
                output.write(row[1][0]+" "+row[1][1]+'\n\n')

def word_bank_exercise(number=5, number_of_files=5):
    """Make word bank execises and write in files"""
    os.makedirs('./word-bank_exercises', exist_ok=True)
    for i in range(0, number_of_files):
        with open('./word_bank_exercises/word_bank{}.txt'.format(i), 'w', encoding='utf-8') as output:
            elements = random.sample(RIGHT_DICTIONARY.items(), number)


def open_collocation_file():
    """Make right dictionary, where key is first component, values -- second"""
    df_collocations = pandas.read_csv('AcademicCollocationList.csv')
    begin_col = df_collocations[['Component I']]
    end_col = df_collocations[['Component II']]
    for begin, end in zip(begin_col.values, end_col.values):
        if '(' not in begin[0] and '(' not in end[0]:
            RIGHT_DICTIONARY[begin[0]] = end[0]


def multiple_choice_exercise(number_inside=10, number_of_files=10, ex_format='txt'):
    """
    Function for calling and writing multiple choice exercises
    :param number_inside: number of exercises inside one document
    :param number_of_files: number of documentts
    :param ex_format: can be txt or xml
    :return:
    """
    os.makedirs('./multiple_choice_{}'.format(ex_format), exist_ok=True)
    for i in range(0, number_of_files):
        with open('./multiple_choice_{}/multiple_choice{}.{}'.format(ex_format, i, ex_format), 'w', encoding='utf-8') as output:
            if ex_format == 'xml': output.write("<quiz>")
            elements = random.sample(RIGHT_DICTIONARY.items(), number_inside)
            for number, (key, value) in enumerate(elements):
                print(number, key, value)
                m_ch_exer = MultipleChoice((key, value))
                sentence = m_ch_exer.find_coll_in_text(1)
                choices = m_ch_exer.make_choices()
                if sentence != None:
                    choices.append(value)
                    if ex_format == 'xml':
                        MultipleChoice.write_in_moodle_xml(number, [sentence, choices, value], output, 'multichoice')
                    else:
                        m_ch_exer.write_in_normal_format(sentence, choices, output)
            if ex_format == 'xml': output.write('</quiz>')


if __name__ == '__main__':
    open_collocation_file()
    #random_match_exercise(number=10, number_of_files=10) #ok
    #make_multiple_choice_ex(number_inside=10, number_of_files=10) #ok
    #wordform_exercise(number=5)

    #open_cloze_exercise(number=5, number_of_files = 5) доделать!
    #word_bank_exercise(number=10, number_of_files=10) доделать нормально. Или из опен-клоз создать

    multiple_choice_exercise(number_inside=5, number_of_files=3, ex_format='txt')