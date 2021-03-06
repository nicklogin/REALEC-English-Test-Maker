__author__ = 'alenush'

""" This script goes through links and takes all lists of academic 
phrases, difficult words and so on. Makes academic lists and dictionaries."""

import urllib.request
from lxml.html import parse
from lxml import etree
import json

class Word_lists:

    def __init__(self):
        self.oxford_words_list = set()
        self.oxford_li = './/ul[@class="result-list1 wordlist-oxford3000 list-plain"]//li//a'
        self.wikipedia_link = 'https://en.wikipedia.org/wiki/Wikipedia:List_of_commonly_misused_English_words'
        self.wordform_link = 'https://simple.wiktionary.org/wiki/Wiktionary:BNC_spoken_freq_0{}'#01,02, 03,04
        self.wordform_link2 = 'http://www.uefap.com/vocab/select/awl.htm'
        self.misspell_dictionary = {}
        self.misued_words_array = []
        self.wordform_dictionary = {}


    def take_academic_wordlist(self):
        """
        Parse oxford word academic list online. Takes words from
        http://www.oxfordlearnersdictionaries.com/wordlist/english/academic/AcademicWordList_sublist_1
        and save in  set self.oxford_words_list
        :return:oxford academic word list set.
        """
        for list in range(1,11):
            tree = parse('http://www.oxfordlearnersdictionaries.com/wordlist/english/academic/AcademicWordList_sublist_{}/'.format(list))
            for ul in tree.findall(self.oxford_li):
                self.oxford_words_list.add(ul.text)
            inner_pages = tree.findall('.//ul[@class="paging_links inner"]//li//a')
            for page in inner_pages[:(len(inner_pages)//2-1)]:
                page_link = page.get('href')
                inside_tree = parse(page_link)
                for ul in inside_tree.findall(self.oxford_li):
                    self.oxford_words_list.add(ul.text)
        return self.oxford_words_list


    def takes_misspel_words(self):
        """
        Takes most misspel words (wikipedia source) and create a dcitionary
        :return: dictionary, where key is a misspelll word and value-array of correct words
        """
        with open('misspell.txt', 'r', encoding='utf-8') as misspell_text:
            words_array = misspell_text.read().split('\n')
            for words in words_array:
                misspell, correct = words.split('->')
                if ',' in correct:
                    correct_words = correct.split(',')
                else: correct_words = [correct]
                self.misspell_dictionary[misspell] = correct_words
        return self.misspell_dictionary


    def takes_misued_words(self):
        """
        Misued words from wikipeia list
        :return: array of arrays
        """
        parser = etree.HTMLParser()
        with urllib.request.urlopen(self.wikipedia_link) as f:
            tree = etree.parse(f, parser)
            for li in tree.findall('.//ul//li'):
                confused_words = []
                for word in li.findall('.//b//a'):
                    confused_words.append(word.text)
                if confused_words!=[]:
                    self.misued_words_array.append(confused_words) #[woman, women]
        return self.misued_words_array

    def takes_wordforms(self):
        """
        Takes the link from wiipedia of wordfirmation.
        Parse the html and save everyhing in the dictionary
        """
        parser = etree.HTMLParser()
        for i in range(1,5):
            print(self.wordform_link.format(i))
            with urllib.request.urlopen(self.wordform_link.format(i)) as f:
                tree = etree.parse(f, parser)
                for li in tree.findall('.//li'):
                    for a in li.findall('./a'):
                        words = []
                        for word in li.findall('.//dl//dd/a'):
                            words.append(word.text)
                        self.wordform_dictionary[a.text] = words

    def write_in_file(self):
        """
        Save the word_formation dictionary in json file.
        """
        with open('wordforms.json', 'w', encoding='utf-8') as my_file:
            json.dump(self.wordform_dictionary, my_file)


if __name__ == '__main__':
    w_list = Word_lists()
    #academic_word_list = w_list.take_academic_wordlist()
    #misspell_dictionary = w_list.takes_misspel_words()
    #misused_words = w_list.takes_misued_words()
    w_list.takes_wordforms()
    print(w_list.wordform_dictionary)
    w_list.write_in_file()
