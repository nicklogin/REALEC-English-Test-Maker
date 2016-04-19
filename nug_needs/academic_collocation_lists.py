import os, re

from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.tokenize import RegexpTokenizer
from nltk import FreqDist
from nltk import bigrams
from nltk.collocations import *
from nltk.corpus import stopwords
import nltk

stop = stopwords.words('english')
numbers = re.compile('[0-9]+')


def make_dictionary(path):
    """
    Make dictionary of all texts in
    :param path: to Categories_new
    """
    token_dict = {}
    for dirpath, dirs, files in os.walk(path):
        for f in files:
            fname = os.path.join(dirpath, f)
            print ("fname=", fname)
            with open(fname) as one_text:
                text = one_text.read().lower()
                tokenizer = RegexpTokenizer(r'\w+')
                text_array = tokenizer.tokenize(text)
                token_dict[f] = ' '.join(text_array)
    return token_dict

def tf_idf_function(token_dictionary, discipline):
    """
    Make tf-idf scores
    :param token_dictionary: dictionary
    :param discipline: string. File name of discipline
    :return: sorted dictionary of discipline words
    """
    my_dictionary = {}
    tf_idf = TfidfVectorizer(stop_words='english')
    tf_idf.fit_transform(token_dictionary.values())
    response = tf_idf.transform([token_dictionary[discipline]])
    feature_names = tf_idf.get_feature_names()
    for col in response.nonzero()[1]:
        if response[0, col] > 0.07: #не знаю почему поставила такой порог. просто на глаз
            my_dictionary[feature_names[col]] = response[0,col]
    return sorted(my_dictionary)


def find_most_freq_words(text_array):
    """Find most frequent words and write in file:
    word, absolute freq, relative freq"""
    clean_text_array = [word for word in text_array if word not in stop and numbers.match(word) == None]
    simple_freq = FreqDist(clean_text_array)
    text_size = len(text_array)
    with open('freq_list_1000.csv', 'w', encoding='utf-8') as freq_file:
        freq_file.write("word,absolute frequency, relative frequency\n")
        for word, freq in simple_freq.most_common(1000):
            freq_file.write("{},{},{}\n".format(word, freq, (freq/text_size)*100))


def find_most_freq_collocations(text_array):
    """Find most frequent collocations and write in file
    """
    bigram_measures = nltk.collocations.BigramAssocMeasures()
    finder = BigramCollocationFinder.from_words(text_array)
    finder.apply_freq_filter(10)
    ignored_words = nltk.corpus.stopwords.words('english')
    finder.apply_word_filter(lambda w: len(w) < 3 or (numbers.match(w) != None) or w.lower() in ignored_words)
    print(finder.nbest(bigram_measures.pmi, 100))

    #my_bigrams = list(bigrams(text_array))
    #freq_dict = FreqDist(my_bigrams)
    #for big, freq in freq_dict.most_common(100):
    #    print(big, freq)

def main(path_to_text):
    """
    Open the file and
    :param path_to_text: path to text of one Disciplline
    :return:
    """
    with open(path_to_text, 'r', encoding='utf-8') as discipline_text:
        text = discipline_text.read().lower()
        tokenizer = RegexpTokenizer(r'\w+')
        text_array = tokenizer.tokenize(text)
        find_most_freq_words(text_array)
        find_most_freq_collocations(text_array)

if __name__ == '__main__':
    path = '../Categories_new/Economics.txt'
    main(path)

    #path = '../Categories_new/'
    #token_dictionary = make_dictionary(path)
    #my_dictionary = tf_idf_function(token_dictionary, 'Business.txt')
    #print(my_dictionary)
