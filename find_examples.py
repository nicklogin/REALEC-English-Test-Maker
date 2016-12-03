# coding: utf-8
import sys, codecs, re, os
from gathering import gathering
from sentencesplit import main as splitting


class Exercise:
    def __init__(self, path_new, path_old):
        self.path_new = path_new
        self.path_old = path_old
        self.error_type = gathering(self.path_new)[0]

    def find_sentences(self):
        anns = [f for f in os.listdir(self.path_old) if f.endswith('.ann')]
        txts = [f for f in os.listdir(self.path_old) if f.endswith('.txt')]
        sent_examples, n = [], 1
        for ann in anns:
            errs = {}
            other_errs = {}
            for line in codecs.open(self.path_old + ann, 'r', 'utf-8').readlines():
                if re.search('^T', line) is not None and 'pos_' not in line:
                    try:
                        t, span, text = line.strip().split('\t')
                    except:
                        continue
                    err = span.split()[0]
                    if err == self.error_type:
                        spans = span.split()[1:]
                        errs[t] = [spans, text]
                    else:
                        spans = span.split()[1:]
                        other_errs[t] = [spans, text]
                elif re.search('^#', line) is not None and 'lemma =' not in line:
                    try:
                        x, t, correction = line.strip().split('\t')
                    except:
                        continue
                    t = t.split()[1]
                    try:
                        errs[t].append(correction)
                    except KeyError:
                        try:
                            other_errs[t].append(correction)
                        except KeyError:
                            continue
                elif re.search('^A', line) is not None and 'Delete' in line:
                    t = line.strip().split('\t')[1].split()[1]
                    try:
                        errs[t].append('')
                    except KeyError:
                        other_errs[t].append('')
                if errs != {}:
                    try:
                        print(ann[:-4].encode('utf-8'))
                        txt = path_old + ann[:-4] + '.txt'
                        content = codecs.open(txt, 'r', 'utf-8').read()
                        splitted = splitting(txt)
                        sentences = [x for x in splitted.split('\n') if x != u'']
                        for sent in sentences:
                            try:
                                sent_spans = (content.index(sent), content.index(sent) + len(sent))
                            except ValueError:
                                continue
                        for t in errs:
                            if int(errs[t][0][0]) >= sent_spans[0] and int(errs[t][0][1]) <= sent_spans[1]:
                                example = sent
                                try:
                                    example = example.replace(errs[t][1], '(' + errs[t][1] + '/' + errs[t][2] + ')', 1)
                                except IndexError:
                                    example = example.replace(errs[t][1], '(' + errs[t][1] + '/no correction)', 1)
                        for t in other_errs:
                            if int(other_errs[t][0][0]) >= sent_spans[0] and int(other_errs[t][0][1]) <= sent_spans[1]:
                                try:
                                    example = example.replace(other_errs[t][1], other_errs[t][2], 1)
                                except IndexError:
                                    continue
                        example = re.sub(' +', ' ', example)
                        if example[0] == ' ':
                            example = example[1].upper() + example[2:]
                            print(str(n) + '.', example.encode('utf-8'))
                            sent_examples.append(example)
                        n += 1
                    except AssertionError:
                        continue

path_new, path_old = sys.argv[1:]
e = Exercise(path_new, path_old)
e.find_sentences()