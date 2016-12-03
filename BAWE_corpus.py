import os, lxml.html
"""Script takes from the BAWE CORPUS xml categories
 and make a big files from the texts sorted by these categories!"""

def extract_categories(path):
    """Function takes the path to folder with xml texts from BAWE
    and collect all Categories and texts. Write in categories dictionary
    :return; dictionary; categories"""
    #categories = {'L1': {}, 'L2':{}}
    L1_categories = {}
    L2_categories = {}
    path = os.path.join(path, 'CORPUS_UTF-8')
    for fname in os.listdir(path):
        if not fname.endswith('xml'):
            continue
        with open(os.path.join(path, fname), 'r', encoding='utf-8') as f:
            html = f.read().replace('<?xml version="1.0" encoding="UTF-8"?>', '')
        root = lxml.html.fromstring(html)
        category = root.xpath('//p[@n="discipline"]/text()')[0]
        mother_tongue = root.xpath('//p[@n="first language"]/text()')[0]
        if mother_tongue == 'English':
            try:
                L1_categories[category].append(fname.split('.')[0])
            except KeyError:
                L1_categories[category] = [fname.split('.')[0]]
        else:
                try:
                    L2_categories[category].append(fname.split('.')[0])
                except KeyError:
                    L2_categories[category] = [fname.split('.')[0]]
    print(L1_categories)
    print(L2_categories)
    return L1_categories, L2_categories


def make_corpora(L1_categories, L2_categories, path):
    """
    Make a folder and compile texts by categories!
    :param categories: dictionary
    :param path: path to folder
    """
    os.makedirs('./L1_L2_categories', exist_ok=True)
    path = os.path.join(path, 'CORPUS_TXT')
    os.makedirs('./L1_L2_categories/L1', exist_ok=True)
    for cat in L1_categories:
        with open('./L1_L2_categories/L1/'+cat + '.txt', 'w', encoding='utf-8') as f:
            for fname in L1_categories[cat]:
                    text = open(os.path.join(path, fname + '.txt'), 'r', encoding='utf-8').read()
                    f.write(text + '\n')
    os.makedirs('./L1_L2_categories/L2', exist_ok=True)
    for cat in L2_categories:
        with open('./L1_L2_categories/L2/' + cat + '.txt', 'w', encoding='utf-8') as f:
            for fname in L2_categories[cat]:
                    text = open(os.path.join(path, fname + '.txt'), 'r', encoding='utf-8').read()
                    f.write(text + '\n')

if __name__ == '__main__':
    path = '/home/alenush/Документы/НУГ/'
    L1_categories, L2_categories = extract_categories(path)
    make_corpora(L1_categories, L2_categories, path)