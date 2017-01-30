__author__ = 'alenush'

import pprint
import random
import json
import os

""" This is a script for exercises on words mostly confused. 
Based on BAWE corpus. XML moodle format as output. """

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
    for_exercise = []
    for element in elements:
        if len(element) > 0:
            one_example = random.choice(element)
            for_exercise.append(one_example)
        if len(for_exercise) > 1:
            for case in for_exercise:
                output.write('{}\t{}\n'.format(case[0], case[1]))
            output.write('=======================\n')

def write_match_ex_in_moodle(output, elements):
    """Write in moodle xml format one doc"""
    for_exercise = []
    # output.write("<quiz>")
    output.write('<question type="matching">\n')
    output.write('<name><text>Match the word</text></name>\n')
    output.write('<questiontext format="html">\n<text><![CDATA[<p>'
                    'Match the words below<br></p>]]></text>\n</questiontext>\n')
    output.write("<defaultgrade>1.0000000</defaultgrade>\n<penalty>0.3333333</penalty>\n"
                        "<hidden>0</hidden>\n<single>true</single>\n<shuffleanswers>true</shuffleanswers>\n"
                        "<correctfeedback format='html'>\n"
                        "<text>Your answer is correct.</text>\n</correctfeedback>\n"
                        "<partiallycorrectfeedback format='html'>\n<text>Your answer is partially correct.</text>\n"
                        "</partiallycorrectfeedback>\n<incorrectfeedback format='html'>\n"
                        "<text>Your answer is incorrect.</text>\n</incorrectfeedback>\n"
                        "<shownumcorrect/>\n")
    for element in elements:
        if len(element) > 0:
            one_example = random.choice(element)
            for_exercise.append(one_example)
        if len(for_exercise) > 1:
            for case in for_exercise:
                # print(case)
                output.write('<subquestion format="html">\n'
                             '<text><![CDATA[<p>{}<br></p>]]></text>\n'
                             '<answer><text><![CDATA[<p>{}<br></p>]]></text></answer>\n</subquestion>\n'.format(case[1].rstrip(), case[0]))
    output.write('</question>\n')
    # output.write("</quiz>")

def find_context(word):
    """Find in corpus sentence with this word"""
    examples = []
    for sentence in corpus:
        if sentence[0].isupper():
            if word in sentence.split():
                word_index = sentence.index(word)
                sentence = sentence[:word_index] + '______' + sentence[word_index+len(word):]
                examples.append((word, sentence))
    return examples

def random_match_exercise(pairs, ex_format='txt'):
    """
    Exercise of type Match the word from right with left column
    Function takes right collocations and randomize them
    :return: rows like: coll1, coll2_wrong, coll2_right
    """
    os.makedirs('./pitra/match_exercises', exist_ok=True)
    with open('./pitra/match_exercises/match_exercises.{}'.format(ex_format), 'w', encoding='utf-8') as output:
            for one_set in pairs:
                one_set_exercise = []
                for word in one_set:
                    example = find_context(word)
                    one_set_exercise.append(example)
                # write_match_exercise(output, one_set_exercise) # Works! text
                write_match_ex_in_moodle(output, one_set_exercise)
                # print(all_examples)
                # if ex_format == 'txt':
                #     write_match_exercise(output, all_examples)
                # else:
                #     write_match_ex_in_moodle(output, all_examples)

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
    random_match_exercise(pairs_array, ex_format='xml')


#1 Match exercise
# word, word => sentence sentence

#2 Multiple choice - ?
# word1, word2 (without extra word2vec hypothesis)
