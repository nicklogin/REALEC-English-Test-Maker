__author__ = 'alenush'

import pandas
import random
import json
import os
from nltk import WordNetLemmatizer
from nltk import word_tokenize
from gensim.models import Word2Vec
import difflib


def choose_corpora(corpus_name):
    if corpus_name == 'bawe' or corpus_name == 'bnc':
        path = '.'
    else:
        path = './Categories_new'
    with open('{}/{}.txt'.format(path,corpus_name), 'r', encoding='utf-8') as source_file:  # This is my corpus (BAWE or BNC)
        global corpus
        corpus = [sentence for sentence in source_file.readlines()]

#========= MATCH EXERCISE =======================

def write_match_exercise(output, elements):
    """
    Write in txt format one exercise
    :param right_col: array of answers
    :param output: io_object
    :param elements: random dictionary
    """
    for key, value in elements:
        output.write('{}, {}, {}\n'.format(key, value))

def write_match_ex_in_moodle(output, examples):
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
    for key, value in examples:
        output.write('<subquestion format="html">\n'
                     '<text><![CDATA[<p>{}<br></p>]]></text>\n'
                     '<answer><text><![CDATA[<p>{}<br></p>]]></text></answer>\n</subquestion>\n'.format(key, value))
    output.write('</question>\n')
    output.write("</quiz>")

def find_context(word):
    """Find in corpus sentence with this word""" #TODO check by lemmas
    sentence = '' # sentence with ____ on the right place
    for sentence in random.sample(corpus, 1): # TODO Check random!
        if word in sentence.split():
            word_index = sentence.index(word)
            sentence = sentence[:word_index] + '______' + sentence[word_index+len(word):]
            print(word, sentence)
    return (word, sentence)

def random_match_exercise(pairs, ex_format='txt'):
    """
    Exercise of type Match the word from right with left column
    Function takes right collocations and randomize them
    :return: rows like: coll1, coll2_wrong, coll2_right
    """
    os.makedirs('./pitra/match_exercises', exist_ok=True)
    with open('./pitra/match_exercises/match_exercises.{}'.format(ex_format), 'w', encoding='utf-8') as output:
            all_examples = [] # [ [(word, sentence), (word, sentence)] ]
            for one_set in pairs:
                one_set_exercise = []
                for word in one_set:
                    example = find_context(word)
                    # print(example)
                    one_set_exercise.append(example)
                all_examples.append(one_set_exercise)
            # print(all_examples)
            # if ex_format == 'txt':
            #     write_match_exercise(output, all_examples)
            # else:
            #     write_match_ex_in_moodle(output, all_examples)

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
        variants = model.most_similar(self.second_col, topn=200)
        choices = []
        for var in variants[170:]:
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


def open_source_file():
    """Make right dictionary, set of confused words"""
    pairs_set = []
    with open('./pitra/complex_pairs.csv', 'r', encoding='utf-8') as pairs:
        for line in pairs.readlines():
            confused_words = line.rstrip().split(';')
            pairs_set.append(confused_words)
    return pairs_set

def multiple_choice_exercise(number_inside=10, number_of_files=10, ex_format='txt'):
    """
    Function for calling and writing multiple choice exercises
    :param number_inside: number of exercises inside one document
    :param number_of_files: number of documents
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
    choose_corpora('bawe')
    pairs_array = open_source_file()

    '''Exercises'''
    #multiple_choice_exercise(number_inside=1, number_of_files=3, ex_format='xml')
    random_match_exercise(pairs_array, ex_format='txt')


#1 Match exercise
# word, word => sentence sentence

#2 Multiple choice - ?
# word1, word2 (without extra word2vec hypothesis)
