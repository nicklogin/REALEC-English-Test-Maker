__author__ = 'alenush'

import pandas
import random
import json
import os
from nltk import WordNetLemmatizer
from nltk import word_tokenize
from gensim.models import Word2Vec
import difflib


RIGHT_DICTIONARY = {} # there are all my collocations here

with open('new_corpus.txt', 'r', encoding='utf-8') as source_file: # This is my corpus (BAWE or BNC)
    corpus = [sentence for sentence in source_file.readlines()]

#========= MATCH EXERCISE =======================

def write_match_exercise(right_col, output, elements):
    """
    Write in txt format one exercise
    :param right_col: array of answers
    :param output: io_object
    :param elements: random dictionary
    """
    for key, value in elements:
        print(key, value)
        random_element = random.choice(right_col)
        output.write('{}, {}, {}\n'.format(key, random_element, value))
        right_col.remove(random_element)

def write_match_ex_in_moodle(output, elements, right_col):
    """Write in moodle xml format one doc"""
    output.write("<quiz>")
    output.write('<question type="matching">\n')
    output.write('<name><text>Match collocation question</text></name>\n')
    output.write('<questiontext format="html">\n<text><![CDATA[<p>'
                    'Match the collocations below<br></p>]]></text>\n</questiontext>\n')
    output.write("<defaultgrade>1.0000000</defaultgrade>\n<penalty>0.3333333</penalty>\n"
                        "<hidden>0</hidden>\n<single>true</single>\n<shuffleanswers>true</shuffleanswers>\n"
                        "<correctfeedback format='html'>\n"
                        "<text>Your answer is correct.</text>\n</correctfeedback>\n"
                        "<partiallycorrectfeedback format='html'>\n<text>Your answer is partially correct.</text>\n"
                        "</partiallycorrectfeedback>\n<incorrectfeedback format='html'>\n"
                        "<text>Your answer is incorrect.</text>\n</incorrectfeedback>\n"
                        "<shownumcorrect/>\n")
    for key, value in elements:
        output.write('<subquestion format="html">\n'
                     '<text><![CDATA[<p>{}<br></p>]]></text>\n'
                     '<answer><text><![CDATA[<p>{}<br></p>]]></text></answer>\n</subquestion>\n'.format(key, value))
    output.write('</question>\n')
    output.write("</quiz>")

def random_match_exercise(number=5, number_of_files=5, ex_format='txt'):
    """
    Exercise of type Match the word from right with left column
    Function takes right collocations and randomize them
    :return: rows like: coll1, coll2_wrong, coll2_right
    """
    os.makedirs('./match_exercises_{}'.format(ex_format), exist_ok=True)
    for i in range(0, number_of_files):
        with open('./match_exercises_{}/match_exercises{}.{}'.format(ex_format, i, ex_format), 'w', encoding='utf-8') as output:
            elements = random.sample(RIGHT_DICTIONARY.items(), number)
            right_col = [paar[1] for paar in elements]
            if ex_format == 'txt':
                write_match_exercise(right_col, output, elements)
            else:
                write_match_ex_in_moodle(output, elements, right_col)

#=========== NORMAL EXERCISES ==========

class Exercise:

    def __init__(self, whole_coll):

        self.collocation = whole_coll[0] + ' ' + whole_coll[1]
        self.first_col = whole_coll[0]
        self.second_col = whole_coll[1]
        self.headword = ''

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

    def find_collocation_moodle_write(self, collocate_part=1, type='open_cloze'):
        """
            Find the word from collocation
            :collocate_part: 1 or 0, 0 -is first part, 1 is second
            Write in Moodle format like: {1:SHORTANSWER:=deeper}
            :type: open_cloze or word_form
        """
        for sentence in corpus:
            sent_coll = self.check_whole_collocation(sentence)  # check all possible variants
            if sent_coll != False:
                new_sentence = []
                if type == 'word_form':
                    for word in word_tokenize(sentence):
                        if word == sent_coll[collocate_part]:
                                new_sentence.append("{1:SHORTANSWER:=%s}" % word)
                                new_sentence.append('(%s)'% self.headword)
                        else:
                            new_sentence.append(word)
                else:
                    print("Here will be open_cloze")
                    print(sentence)
                return ' '.join(new_sentence)

    def check_whole_collocation(self, sentence):
        """
        Generate part1 + part2 possible variants
        :param col
        :return: return collocation -- (col1, col2) or False
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

    def write_in_moodle_format(self, output, sentence, type):
        """Write in moodle format one word_form exercise"""
        output.write('<quiz>\n'
                         '<question type="cloze"> \n'
                         '<name><text>{}</text></name>\n'.format(type))
        output.write(
                '<questiontext format="html"><text><![CDATA[<p>{}</p>]]></text></questiontext>\n'.format(sentence))
        output.write('<generalfeedback format="html">\n'
                         '<text/></generalfeedback><penalty>0.3333333</penalty>\n'
                         '<hidden>0</hidden>\n</question>\n')
        output.write('</quiz>')


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

    def find_collocation(self):
        """
        Find whole collocation. make gap from it and safe collocate as a write answer.
        :return: sentence and tuple = (col1, col2)
        """
        for sentence in corpus:
            col = self.check_whole_collocation(sentence)
            if col != False:
                split_sent = sentence.split(' ')
                index = [ num for num, part in enumerate(split_sent) if part == col[0]]
                sent_first = split_sent[1:index[0]]
                sent_second = split_sent[index[0]+2:]
                sentence = "{} ".format(' '.join(sent_first))+\
                           "{1:SHORTANSWER:=%s %s}"%(split_sent[index[0]],split_sent[index[0]+1])+\
                           " {}".format(' '.join(sent_second))
                return sentence


class Word_Bank_Cloze(Exercise):

    def __init__(self, whole_coll):
        super().__init__(whole_coll)

    def find_collocation(self, n):
        """
        Find whole collocation. make gap from it and safe collocate as a write answer.
        :return: sentence and tuple = (col1, col2)
        """
        for sentence in corpus:
            col = self.check_whole_collocation(sentence)
            if col != False:
                split_sent = sentence.split(' ')
                index = [num for num, part in enumerate(split_sent) if part == col[0]]
                sent_first = split_sent[1:index[0]]
                sent_second = split_sent[index[0]+2:]
                sentence = "{} ".format(' '.join(sent_first))+\
                           "[[%s]]"%(n+1)+\
                           " {}".format(' '.join(sent_second))
                return sentence, (split_sent[index[0]], split_sent[index[0]+1])

    @staticmethod
    def write_in_moodle_xml(output, sentence, answers):
        output.write('<quiz>\n')
        output.write('<question type="ddwtos">\n')
        output.write('<name><text>Word bank</text></name>\n'
                     '<questiontext format="html">\n<text><![CDATA[<p>'
                     '{}<br></p>]]></text>\n</questiontext>\n'.format(sentence))
        output.write('<generalfeedback format="html">\n<text/></generalfeedback>\n'
                     '<defaultgrade>1.0000000</defaultgrade>\n'
                     '<penalty>0.3333333</penalty>\n'
                     '<hidden>0</hidden>\n'
                     '<shuffleanswers>0</shuffleanswers>\n'
                     '<correctfeedback format="html"><text>Your answer is correct.</text></correctfeedback>\n'
                     '<partiallycorrectfeedback format="html"><text>Your answer is partially correct.</text></partiallycorrectfeedback>\n'
                     '<incorrectfeedback format="html"><text>Your answer is incorrect.</text></incorrectfeedback>\n<shownumcorrect/>\n')
        for answer in answers:
            output.write('<dragbox>\n<text>{}</text>\n<group>1</group>\n</dragbox>\n'.format(answer))
        output.write('</question>\n</quiz>')


class WordFormExercise(Exercise):

    def __init__(self, whole_coll):
        super().__init__(whole_coll)
        self.headword = ''

        with open('wordforms.json', 'r', encoding="utf-8") as dictionary:
            self.wf_dictionary = json.load(dictionary) #{'headword':[words,words,words]}

    def check_headword(self, my_col):
        """Return headword from the dictionary"""
        for key, value in self.wf_dictionary.items():
            headword = [val for val in value if val == my_col]
            if len(headword)>0:
                return key

    def make_sentence(self):
        """
        Find headword and write a sentence in moodle format. {1:SHORTANSWER:=deeper} (deep)
        return: string - sentence
        """
        headword = self.check_headword(self.first_col)
        self.headword = headword
        if headword != None:
            sentence = self.find_collocation_moodle_write(collocate_part=0, type='word_form')
            return sentence

def wordform_exercise(number=5, ex_format='txt'):
    """Make word formation exercise in moodle format and just text"""
    os.makedirs('./wordforms_exercises_{}'.format(ex_format), exist_ok=True)
    for i in range(0, number):
        with open('./wordforms_exercises_{}/wordform{}.{}'.format(ex_format, i, ex_format), 'w', encoding='utf-8') as output:
            elements =  random.sample(RIGHT_DICTIONARY.items(), number) # actually it's strange. do not need number, but may be error
            for key, value in elements:
                wf_ex = WordFormExercise((key, value))
                sentence = wf_ex.make_sentence()
                if sentence != None:
                    if ex_format == 'txt':
                        output.write(sentence + '\n')
                    else:
                        wf_ex.write_in_moodle_format(output, sentence, type="Word formation")
                    break

def open_cloze_exercise(number=5, ex_format='txt'):
    """Make open cloze execises and write in files"""
    os.makedirs('./open_cloze_exercises_{}'.format(ex_format), exist_ok=True)
    for i in range(0, number):
        with open('./open_cloze_exercises_{}/open_cloze{}.{}'.format(ex_format,i,ex_format), 'w', encoding='utf-8') as output:
            elements = random.sample(RIGHT_DICTIONARY.items(), number)
            for paar in elements:
                op_ex = OpenCloze((paar[0], paar[1]))
                try:
                    sentence = op_ex.find_collocation() #TODO: not all forms are checked
                    if ex_format == 'xml':
                        op_ex.write_in_moodle_format(output, sentence, type="Open Cloze")
                    else:
                        output.write(sentence+'\n')
                    break
                except:
                    print("No sentence with collocation")


def word_bank_exercise(number=5, number_of_files=2, ex_format="txt"):
    """Make word bank execises and write in files"""
    os.makedirs('./word_bank_exercises_{}'.format(ex_format), exist_ok=True)
    for i in range(0, number_of_files):
        with open('./word_bank_exercises_{}/word_bank{}.{}'.format(ex_format, i, ex_format), 'w', encoding='utf-8') as output:
            elements = random.sample(RIGHT_DICTIONARY.items(), number)
            answers, ex_text = [], ''
            for n, paar in enumerate(elements):
                print(paar)
                op_ex = Word_Bank_Cloze((paar[0], paar[1]))
                sentence, answer = op_ex.find_collocation(n)
                answers.append(answer[0]+" "+answer[1])
                ex_text += sentence + '\n'
            if ex_format == 'xml':
                Word_Bank_Cloze.write_in_moodle_xml(output, ex_text, answers)
            else:
                output.write(ex_text + '\n')
                output.write("Possible answers: "+', '.join(answers)+'\n')


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
            if ex_format == 'xml': output.write("<quiz>\n")
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
    #Exercises:
    multiple_choice_exercise(number_inside=5, number_of_files=3, ex_format='txt')
    random_match_exercise(number=7, number_of_files=2, ex_format='txt')
    wordform_exercise(number=5, ex_format='xml')
    open_cloze_exercise(number=5, ex_format='xml')
    word_bank_exercise(number=5, number_of_files = 3, ex_format='xml')

#:todo make a template of xml not to write in 100500 times!
#word bank and open cloze -- test! find little bugs!