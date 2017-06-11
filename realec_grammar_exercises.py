import sys, codecs, re, os, traceback
from collections import defaultdict
import shutil
import random
import json

"""Script that generates grammar exercises from REAELEC data """

class Exercise:
    def __init__(self, path_to_realecdata, error_type, exercise_type, bold, context):

        """"
        :param error_type: 'Tense_choice', 'Tense_form', 'Voice_choice', 'Voice_form', 'Number
        :param exercise_type: multiple_choice, word_formation, short_answer, open_cloze
        """
        self.path_new = './processed_texts/'
        self.path_old = path_to_realecdata
        self.error_type = error_type
        self.exercise_type = exercise_type
        self.current_doc_errors = defaultdict()
        self.bold = bold
        self.context = context
        self.headword = ''
        self.write_func = {
            "short_answer": self.write_sh_answ_exercise,
            "multiple_choice": self.write_multiple_ch,
            "word_form": self.write_open_cloze,
            "open_cloze": self.write_open_cloze
        }
        os.makedirs('moodle_exercises', exist_ok=True)
        os.makedirs('processed_texts', exist_ok=True)
        with open('./nug_needs/wordforms.json', 'r', encoding="utf-8") as dictionary:
            self.wf_dictionary = json.load(dictionary)  # {'headword':[words,words,words]}

    def find_errors_indoc(self, line, error_ind):
        """
        Find all T... marks and save in dictionary.
        Format: {"T1":{'Error':err, 'Index':(index1, index2), "Wrong":text_mistake}}
        """
        if re.search('^T', line) is not None and 'pos_' not in line:
            try:
                t, span, text_mistake = line.strip().split('\t')
                err, index1, index2 = span.split()
                self.current_doc_errors[t] = {'Error':err, 'Index':(int(index1), int(index2)), "Wrong":text_mistake}
                return (int(index1), int(index2))
            except:
                #print (''.join(traceback.format_exception(*sys.exc_info())))
                print("Something wrong! No Notes probably", line)

    def validate_answers(self, answer):
        # TO DO: multiple variants?
        if answer.upper() == answer:
            answer = answer.lower()
        answer = answer.strip('\'"')
        answer = re.sub(' ?\(.*?\) ?','',answer)
        if '/' in answer:
            answer = answer.split('/')[0]
        if ' OR ' in answer:
            answer = answer.split(' OR ')[0]
        if ' or ' in answer:
            answer = answer.split(' or ')[0]
        if answer.strip('? ') == '':
            return None
        return answer

    def find_answers_indoc(self, line):
        if re.search('^#', line) is not None and 'lemma =' not in line:
            try:
                number, annotation, correction = line.strip().split('\t')
                t_error = annotation.split()[1]
                if self.current_doc_errors.get(t_error):
                    validated = self.validate_answers(correction)
                    if validated is not None:
                        self.current_doc_errors[annotation.split()[1]]['Right'] = validated
            except:
                #print (''.join(traceback.format_exception(*sys.exc_info())))
                print("Something wrong! No Notes probably", line)

    def find_delete_seqs(self, line):
        if re.search('^A', line) is not None and 'Delete' in line:
            t = line.strip().split('\t')[1].split()[1]
            if self.current_doc_errors.get(t):
                self.current_doc_errors[t]['Delete'] = 'True'

    def make_data_ready_4exercise(self):
        """ Collect errors info """
        anns = [f for f in os.listdir(self.path_old) if f.endswith('.ann')]
        for ann in anns:
            print(ann)
            self.error_intersects = set()
            error_ind = []
            with open(self.path_old + ann, 'r', encoding='utf-8') as ann_file:
                for line in ann_file.readlines():
                    ind = self.find_errors_indoc(line,error_ind)
                    if ind is not None:
                        if ind in error_ind:
                            self.error_intersects.add(ind)
                        else:
                            error_ind.append(ind)
                    self.find_answers_indoc(line)
                    self.find_delete_seqs(line)
            self.embedded,self.overlap = self.find_embeddings(error_ind)
            self.make_one_file(ann.split('.')[0])
            self.current_doc_errors.clear()

    def find_embeddings(self,indices):
        indices.sort(key=lambda x: (x[0],-x[1]))
        embedded = []
        overlap = []
        for i in range(1,len(indices)):
            find_emb = [x for x in indices if (x[0] <= indices[i][0] and x[1] > indices[i][1]) or \
                                              (x[0] < indices[i][0] and x[1] >= indices[i][1])]
            if find_emb:
                embedded.append(indices[i])
            elif indices[i][0] < indices[i-1][1]:
                overlap.append(indices[i])
        return embedded, overlap
        
                

    def make_one_file(self, filename):
        """
        Makes file with current types of errors. all other errors checked.
        :param filename: name of the textfile
        return: nothing. just write files in dir <<processed_texts>>
        """
        with open(self.path_new+filename+'.txt', 'w', encoding='utf-8') as new_file:
            with open(self.path_old+filename+'.txt', 'r', encoding='utf-8') as text_file:
                one_text = text_file.read()
                not_to_write_sym = 0
                for i, sym in enumerate(one_text):
                    intersects = []
                    for t_key, dic in self.current_doc_errors.items():
                        if dic.get('Index')[0] == i:
                            if dic.get('Index') in self.error_intersects:
                                intersects.append(dic)
                                continue
                            if dic.get('Index') in self.embedded or dic.get('Index') in self.overlap:
                                continue
                            if dic.get('Right'):
                                indexes_comp = dic.get('Index')[1] - dic.get('Index')[0]
                                if dic.get('Error') in self.error_type:
                                    new_file.write("*"+str(dic.get('Right'))+'*'+str(indexes_comp)+'*')
                                else:
                                    new_file.write(dic.get('Right') +
                                                   '#'+str(indexes_comp)+ '#')
                            else:
                                if dic.get('Delete'):
                                    indexes_comp = dic.get('Index')[1] - dic.get('Index')[0]
                                    new_file.write("#DELETE#"+str(indexes_comp)+"#")
                    if intersects:
                        needed_error_types = [x for x in intersects if x['Error'] in self.error_type]
                        if needed_error_types and 'Right' in needed_error_types[-1]:
                            saving = needed_error_types[-1]
                            intersects.remove(saving)
                            to_change = intersects[-1]
                            if 'Right' not in to_change or to_change['Right'] == saving['Right']:
                                indexes_comp = saving['Index'][1] - saving['Index'][0]
                                new_file.write("*"+str(saving['Right'])+'*'+str(indexes_comp)+'*')
                            else: 
                                indexes_comp = len(to_change['Right'])
                                not_to_write_sym = saving['Index'][1] - saving['Index'][0]
                                new_file.write("*"+str(saving['Right'])+'*'+str(indexes_comp)+'*'+to_change['Right'])
                        else:
                            if 'Right' in intersects[-1]:
                                if 'Right' in intersects[-2]:
                                    indexes_comp = len(intersects[-2]['Right'])
                                    not_to_write_sym = intersects[-1]['Index'][1] - intersects[-1]['Index'][0]
                                    new_file.write(intersects[-1]['Right'] + '#'+str(indexes_comp)+ '#' + intersects[-2]['Right'])
                                else:
                                    indexes_comp = intersects[-1]['Index'][1] - intersects[-1]['Index'][0]
                                    new_file.write(intersects[-1]['Right'] + '#'+str(indexes_comp)+ '#')
                    if not not_to_write_sym:            
                        new_file.write(sym)
                    else:
                        not_to_write_sym -= 1

    # ================Write Exercises to the files=================

    def find_choices(self, right, wrong): #TODO @Kate, rewrite this function
        """
        Finds two more choices for Multiple Choice exercise.
        :param right:
        :param wrong:
        :return: array of four choices (first is always right)
        """
        choices = [right, wrong]
        for key, value in self.wf_dictionary.items():
            if right == key:
                [choices.append(v) for v in value if v != wrong]
            elif right in value:
                [choices.append(v) for v in value if v != wrong and v != right]
        return choices[:4]

    def check_headform(self, word):
        """Take initial fowm - headform of the word"""
        for key, value in self.wf_dictionary.items():
            headword = [val for val in value if val == word]
            if len(headword)>0:
                return key

    def create_sentence_function(self, new_text):
        """
        Makes sentences and write answers for all exercise types
        :return: array of good sentences. [ (sentences, [right_answer, ... ]), (...)]
        """
        good_sentences = []
        sentences = [''] + new_text.split('. ')
        for sent1, sent2, sent3 in zip(sentences, sentences[1:], sentences[2:]):
            if '*' in sent2:
                try:
                    sent, right_answer, index, other = sent2.split('*')
                    wrong = other[:int(index)]
                    new_sent, answers = '', []
                    if self.exercise_type == 'short_answer':
                        if self.bold:
                            new_sent = sent + '<b>' + wrong + '</b>' + other[int(index):] + '.'
                        else:
                            new_sent = sent + wrong + other[int(index):] + '.'
                        answers = [right_answer]
                    elif self.exercise_type == 'open_cloze':
                        new_sent = sent + "{1:SHORTANSWER:=%s}" % right_answer + other[int(index):] + '.'
                        answers = [right_answer]
                    elif self.exercise_type == 'word_form':
                        new_sent = sent + "{1:SHORTANSWER:=%s}" % right_answer + ' (' +\
                               self.check_headform(right_answer) + ')' + other[int(index):] + '.'
                        answers = [right_answer]
                    elif self.exercise_type == 'multiple_choice':
                        new_sent = sent + "_______ " + other[int(index):] + '.'
                        answers = self.find_choices(right_answer, wrong)
                except:
                    split_sent = sent2.split('*')
                    n = (len(split_sent) - 1) / 3
                    try:
                        chosen = random.randint(0,n-1)
                    except:
                        print('Some issues with markup, skipping:',sent2)
                        continue
                    new_sent,answers = '',[]
                    for i in range(0,len(split_sent),3):
                        if len(split_sent[i:i+4]) > 1:
                            sent, right_answer, index, other = split_sent[i],split_sent[i+1],split_sent[i+2],split_sent[i+3]
                            if self.exercise_type == 'open_cloze' or self.exercise_type == 'word_form':
                                if self.exercise_type == 'open_cloze':
                                    new_sent += "{1:SHORTANSWER:=%s}" % right_answer + other[int(index):]
                                elif self.exercise_type == 'word_form':
                                    new_sent += "{1:SHORTANSWER:=%s}" % right_answer + ' (' +\
                                        self.check_headform(right_answer) + ')' + other[int(index):]                               
                            else:
                                if i == chosen*3:
                                    wrong = other[:int(index)]
                                    if self.exercise_type == 'short_answer':
                                        if self.bold:
                                            new_sent += '<b>' + wrong + '</b>' + other[int(index):]
                                        else:
                                            new_sent += wrong + other[int(index):]
                                        answers = [right_answer]
                                    elif self.exercise_type == 'multiple_choice':
                                        new_sent += "_______ " + other[int(index):]
                                        answers = self.find_choices(right_answer, wrong)
                                else:
                                    new_sent += right_answer + other[int(index):]
                            if i == 0:
                                new_sent = sent + new_sent
                        else:
                            new_sent = new_sent + '.'
                if sent1 and sent3 and self.context: # fixed sentences beginning with a dot
                    text = sent1 + '. ' + new_sent + ' ' + sent3 + '.'
                elif sent3 and self.context:
                    text = new_sent + ' ' + sent3 + '.'
                else:
                    text = new_sent
                text = re.sub(' +',' ',text)
                if '*' not in text:
                    good_sentences.append((text, answers))
        return good_sentences

    def write_sh_answ_exercise(self, sentences):
        pattern = '<question type="shortanswer">\n\
                    <name>\n\
                    <text>Grammar realec. Short answer {}</text>\n\
                     </name>\n\
                <questiontext format="html">\n\
                <text><![CDATA[{}]]></text>\n\
             </questiontext>\n\
        <answer fraction="100">\n\
        <text><![CDATA[{}]]></text>\n\
        <feedback><text>Correct!</text></feedback>\n\
        </answer>\n\
        </question>\n'
        with open('./moodle_exercises/{}_{}.xml'.format(self.error_type, self.exercise_type), 'w', encoding='utf-8') as moodle_ex:
            moodle_ex.write('<quiz>\n')
            for n, ex in enumerate(sentences):
                moodle_ex.write((pattern.format(n, ex[0], ex[1][0])).replace('&','and'))
            moodle_ex.write('</quiz>')
        with open('./moodle_exercises/{}_{}.txt'.format(self.error_type, self.exercise_type), 'w', encoding='utf-8') as plait_text:
            for ex in sentences:
                plait_text.write(ex[1][0]+'\t'+ex[0]+'\n\n')

    def write_multiple_ch(self, sentences):
        pattern = '<question type="multichoice">\n \
        <name><text>Grammar realec. Multiple Choice question {} </text></name>\n \
        <questiontext format = "html" >\n <text> <![CDATA[ <p> {}<br></p>]]></text>\n</questiontext>\n\
        <defaultgrade>1.0000000</defaultgrade>\n<penalty>0.3333333</penalty>\n\
        <hidden>0</hidden>\n<single>true</single>\n<shuffleanswers>true</shuffleanswers>\n\
        <answernumbering>abc</answernumbering>\n<correctfeedback format="html">\n\
        <text>Your answer is correct.</text>\n</correctfeedback>\n\
        <partiallycorrectfeedback format="html">\n<text>Your answer is partially correct.</text>\n\
        </partiallycorrectfeedback>\n<incorrectfeedback format="html">\n\
        <text>Your answer is incorrect.</text>\n</incorrectfeedback>\n'

        with open('./moodle_exercises/{}_{}.xml'.format(self.error_type, self.exercise_type), 'w', encoding='utf-8') as moodle_ex:
            moodle_ex.write('<quiz>\n')
            for n, ex in enumerate(sentences):
                moodle_ex.write((pattern.format(n, ex[0])).replace('&','and'))
                for n, answer in enumerate(ex[1]):
                    correct = 0
                    if n == 0:
                        correct = 100
                    moodle_ex.write('<answer fraction="{}" format="html">\n<text><![CDATA[<p>{}<br></p>]]>'
                                    '</text>\n<feedback format="html">\n</feedback>\n</answer>\n'.format(correct, answer))
                moodle_ex.write('</question>\n')
            moodle_ex.write('</quiz>')
        with open('./moodle_exercises/{}_{}.txt'.format(self.error_type, self.exercise_type), 'w',
                  encoding='utf-8') as plait_text:
            for ex in sentences:
                plait_text.write(ex[0] + '\n' + '\t'.join(ex[1]) + '\n\n')


    def write_open_cloze(self, sentences):
        """:param type: Word form or Open cloze"""
        type = ''
        if self.exercise_type == 'word_form':
            type = "Word form"
        elif self.exercise_type == 'open_cloze':
            type = "Open Cloze"
        pattern = '<question type="cloze"><name><text>Grammar realec. {} {}</text></name>\n\
                     <questiontext format="html"><text><![CDATA[<p>{}</p>]]></text></questiontext>\n''<generalfeedback format="html">\n\
                     <text/></generalfeedback><penalty>0.3333333</penalty>\n\
                     <hidden>0</hidden>\n</question>\n'
        with open('./moodle_exercises/{}_{}.xml'.format(self.exercise_type, self.exercise_type), 'w', encoding='utf-8') as moodle_ex:
            moodle_ex.write('<quiz>\n')
            for n, ex in enumerate(sentences):
                moodle_ex.write((pattern.format(type, n, ex[0])).replace('&','and'))
            moodle_ex.write('</quiz>')
        with open('./moodle_exercises/{}_{}.txt'.format(self.error_type, self.exercise_type), 'w', encoding='utf-8') as plait_text:
            for ex in sentences:
                plait_text.write(ex[0]+'\n\n')

    def make_exercise(self):
        """Write it all in moodle format and txt format"""
        all_sents = []
        for f in os.listdir(self.path_new):
            new_text = ''
            with open(self.path_new + f,'r', encoding='utf-8') as one_doc:
                text_array = one_doc.read().split('#')
                current_number = 0
                for words in text_array:
                    words = words.replace('\n', ' ').replace('\ufeff', '')
                    if re.match('^[0-9]+$', words):
                        if words != '':
                            current_number = int(words)
                    elif words == 'DELETE':
                        current_number = 0
                    else:
                        new_text += words[current_number:]
                        current_number = 0
            if '*' in new_text:
                all_sents += self.create_sentence_function(new_text)
        self.write_func[self.exercise_type](all_sents)

        shutil.rmtree('./processed_texts/')

if __name__ == "__main__":

    path_to_data = './IELTS2015/'
    e = Exercise(path_to_data, 'Tense_choice', 'open_cloze', bold=True, context=False)
    e.make_data_ready_4exercise()

    e.make_exercise()
