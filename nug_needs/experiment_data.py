#__author__ = 'alenush'

import pandas
import matplotlib.pyplot as plt
import numpy as np

data = pandas.read_csv('trainers.csv')

gold_row = []
gold_standard = {'BNC':[], 'BAWE':[], "Original":[]}

for row in data.iloc[0][2:38]:
    gold_row.append(row)

gold_standard["BNC"] = gold_row[:4] + gold_row[12:16] + gold_row[24:28]
gold_standard["BAWE"] = gold_row[4:8] + gold_row[16:20] + gold_row[28:32]
gold_standard["Original"] = gold_row[8:12] + gold_row[20:24] + gold_row[32:36]

print(gold_standard)

students_answers = {}

for i in range(1,23):
    answers = []
    for st_rows in data.iloc[i][2:38]:
        answers.append(st_rows.lower())
    students_answers[data.iloc[i][1]] = answers

for_mean = {'BNC':[], "BAWE":[], 'Origin':[]}
print(len(students_answers))
for key, value in students_answers.items():
    print("Student",key)
    bnc, bawe, origin = 0,0,0
    bnc_answ = value[:4] + value[12:16] + value[24:28]
    bawe_answers = value[4:8] + value[16:20] + value[28:32]
    origin_answers = value[8:12] + value[20:24] + value[32:36]
    for gold, answer in zip(gold_standard['BNC'], bnc_answ):
        if answer in gold:
            bnc +=1
    for gold, answer in zip(gold_standard['BAWE'], bawe_answers):
        if answer in gold:
            bawe +=1
    for gold, answer in zip(gold_standard['Original'], origin_answers):
        if answer in gold:
            origin +=1
    print(bnc/len(bnc_answ)*100, bawe/len(bnc_answ)*100, origin/len(bnc_answ)*100)
    for_mean['BNC'].append(bnc/len(bnc_answ)*100)
    for_mean['BAWE'].append(bawe/len(bnc_answ)*100)
    for_mean['Origin'].append(origin/len(bnc_answ)*100)

print(for_mean)
labels = []
for key, value in for_mean.items():
    print(key, np.mean(value), max(value), min(value))


