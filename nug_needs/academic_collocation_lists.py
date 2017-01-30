import os, re
from math import sqrt

from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.tokenize import RegexpTokenizer
from nltk import FreqDist
from nltk import bigrams
from nltk.collocations import *
from nltk.corpus import stopwords
import nltk

class Frequencies:

    def __init__(self, path, discipline):
        self.path = path
        self.discipline = discipline
        self.discipline_name = discipline.split('.')[0]
        self.simple_freq = {}
        self.tf_idf_dict = {}
        self.token_dict = {} # 'Economics': 'text'
        self.stop = stopwords.words('english')
        self.numbers = re.compile('[0-9]+')
        self.discipline_text = []
        self.bigrams_dictionary = {}

    def make_dictionary(self):
        """
        Make dictionary of all texts {'Category': "text"}
        :param path: to Categories_new
        """
        for dirpath, dirs, files in os.walk(self.path):
            for f in files:
                fname = os.path.join(dirpath, f)
                print ("fname=", fname)
                with open(fname) as one_text:
                    text = one_text.read().lower()
                    tokenizer = RegexpTokenizer(r'\w+')
                    text_array = tokenizer.tokenize(text)
                    self.token_dict[f] = ' '.join(text_array)
        return self.token_dict

    def tf_idf_function(self):
        """
        Make tf-idf scores
        :param discipline: string. File name of discipline
        :return: sorted dictionary of discipline words
        """
        tf_idf = TfidfVectorizer(stop_words='english')
        tf_idf.fit_transform(self.token_dict.values())
        response = tf_idf.transform([self.token_dict[self.discipline]])
        feature_names = tf_idf.get_feature_names()
        for col in response.nonzero()[1]:
            #if response[0, col] > 0.07:
                self.tf_idf_dict[feature_names[col]] = response[0,col]
        return self.tf_idf_dict

    def make_bigrams_dictionary(self):
        """Make bigrams frequent dictionary"""
        my_bigrams = list(bigrams(self.discipline_text))
        self.bigrams_dictionary = FreqDist(my_bigrams)
    #for big, freq in freq_dict.most_common(100):
    #    print(big, freq)

    def find_most_freq_words(self):
        """Find most frequent words and write in file:
        word, absolute freq, relative freq, tf-idf score"""
        clean_text_array = [word for word in self.discipline_text \
                            if word not in self.stop and self.numbers.match(word) == None]
        self.simple_freq = FreqDist(clean_text_array)
        text_size = len(self.discipline_text)
        with open('freq_list_1000_{}.csv'.format(self.discipline_name), 'w', encoding='utf-8') as freq_file:
            freq_file.write("word,absolute frequency,relative frequency,tf-idf score\n")
            for word, freq in self.simple_freq.most_common(1000):
                try:
                    tf_idf_score = self.tf_idf_dict[word]
                except:
                    tf_idf_score = 'No data'
                freq_file.write("{},{},{},{}\n".format(word, freq, (freq/text_size)*100, tf_idf_score))

    def find_most_freq_collocations(self):
        """Find most frequent collocations and write in file
        """
        bigram_measures = nltk.collocations.BigramAssocMeasures()
        finder = BigramCollocationFinder.from_words(self.discipline_text)
        finder.apply_freq_filter(10)
        finder.apply_word_filter(lambda w: len(w) < 3 or (self.numbers.match(w) != None) or w.lower() in self.stop)
        scored_llog = finder.score_ngrams(bigram_measures.likelihood_ratio)
        scored_pmi = finder.score_ngrams(bigram_measures.pmi)
        #score_raw = finder.score_ngrams(bigram_measures.raw_freq)
        return scored_pmi, scored_llog

    def write_in_file_collocations(self, pmi, llog, discipline):
        """
        Write: col1, col2, freq1, fre2, relative freq_collocation, absolute freq,
        pmi_score, llog_score.
        :return:
        """
        with open("collocation_freq_{}.csv".format(discipline), 'w', encoding='utf-8') as output_file:
            output_file.write('collocate1,collocate2,freq_col1,freq_col2,absolute_col_freq,relative_col_freq,pmi_score,llog_score,t-score\n')
            llog_score = 0
            bigram_freq = 0
            for ((col1, col2), pmi_score) in pmi:
                for ((col1_1, col2_1),likelihood) in llog:
                    if col1 == col1_1 and col2 == col2_1:
                        llog_score = likelihood
                for col1_2, col2_2 in self.bigrams_dictionary.keys():
                    if col1 == col1_2 and col2 == col2_2:
                        bigram_freq = self.bigrams_dictionary[(col1_2, col2_2)]
                t_score = (bigram_freq-(self.simple_freq[col1]*self.simple_freq[col2])/len(self.simple_freq))/sqrt(bigram_freq)
                output_file.write('{},{},{},{},{},{},{},{},{}\n'.format(col1,col2, self.simple_freq[col1], self.simple_freq[col2],
                      bigram_freq, (bigram_freq/len(self.bigrams_dictionary))*100, pmi_score, llog_score, t_score))

    def open_file(self):
        """
        Open the file and
        :param path_to_text: path to text of one Discipline
        :return: discipline_text array
        """
        with open(self.path+self.discipline, 'r', encoding='utf-8') as discipline_text:
            text = discipline_text.read().lower()
            tokenizer = RegexpTokenizer(r'\w+')
            self.discipline_text = tokenizer.tokenize(text)
            return self.discipline_text

def check_all_files(path):
    for discipline in os.listdir(path):
        freq_object = Frequencies(path, discipline)
        token_dictionary = freq_object.make_dictionary()
        my_dictionary = freq_object.tf_idf_function()

        freq_object.open_file()
        freq_object.find_most_freq_words()
        freq_object.make_bigrams_dictionary()
        pmi,llog = freq_object.find_most_freq_collocations()
        freq_object.write_in_file_collocations(pmi, llog, discipline.split('.')[0])


if __name__ == '__main__':
    path = '../L2_new/'
    check_all_files(path)