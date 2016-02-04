# coding: utf-8
import codecs, sys, os, re

def gathering(path):
    error_freq = {}

    anns = [f for f in os.listdir(path) if f.endswith('.ann')]
    for ann in anns:
	content = codecs.open(path + ann, 'r', 'utf-8')
        for line in content.readlines():
	    if re.search('^T', line) is not None:
		error_type = line.split('\t')[1].split()[0]
		try:
		    error_freq[error_type] += 1
		except KeyError:
		    error_freq[error_type] = 1
    error_types = []
    max_freq = max(error_freq.values())
    for k in error_freq.keys():
	if error_freq[k] == max_freq:
    	    error_types.append(k)
    return error_types