import os, lxml.html
"""Script takes from the BAWE CORPUS xml categories
 and make a big files from the texts sorted by these categories!"""

def extract_categories(path):
    """Function takes the path to folder with xml texts from BAWE
    and collcet all Categories and texts
    Write in categories dictionary
    :return; dictionary; categories"""
    categories = {}
    path = os.path.join(path, 'CORPUS_UTF-8')
    for fname in os.listdir(path):
        if not fname.endswith('xml'):
            continue
        # print(fname)
        with open(os.path.join(path, fname), 'r', encoding='utf-8') as f:
            html = f.read().replace('<?xml version="1.0" encoding="UTF-8"?>', '')
        root = lxml.html.fromstring(html)
        category = root.xpath('//p[@n="discipline"]/text()')[0]
        try:
            categories[category].append(fname.split('.')[0])
        except KeyError:
            categories[category] = [fname.split('.')[0]]
    return categories


def make_corpora(categories, path):
    """
    Make a folder and compile texts by categories!
    :param categories: dictionary
    :param path: path to folder
    """
    os.makedirs('./Categories', exist_ok=True)
    path = os.path.join(path, 'CORPUS_TXT')
    for cat in categories:
        print(cat)
        with open('./Categories/'+cat + '.txt', 'w', encoding='utf-8') as f:
            for fname in categories[cat]:
                text = open(os.path.join(path, fname + '.txt'), 'r', encoding='utf-8').read()
                f.write(text + '\n')

if __name__ == '__main__':
    path = '/home/alenush/Документы/НУГ/'
    categories = extract_categories(path)
    make_corpora(categories, path)