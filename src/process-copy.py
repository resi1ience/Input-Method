import re
import os
import json
import tqdm
import pypinyin
import argparse
import time

T1 = time.time()

parser = argparse.ArgumentParser()

parser.add_argument('-c', '--corpus', help='corpus list', nargs='+', type=str, required=True)
parser.add_argument('-py', '--pinyin', help='pinyin to hanzi table', required=True)
parser.add_argument('-e', '--emit', help='calculate emission or not', default='no', required=False)
parser.add_argument('-t', '--three', help='calculate 3-gram or not', default='no', required=False)
parser.add_argument('-igth', '--ignorethree', help='ignore 3 word below count', default=1, required=False)
parser.add_argument('-s', '--skip2', help='calculate skip 2-gram or not', default='no', required=False)
parser.add_argument('-p', '--parse', help='parse comma... or not', default='yes', required=False)

args = parser.parse_args()

# assert args.corpus == 'sina' or args.corpus == 'sina_and_smp'
assert args.emit == 'yes' or args.emit == 'no'
assert args.three == 'yes' or args.three == 'no'
assert args.skip2 == 'yes' or args.skip2 == 'no'
assert args.parse == 'yes' or args.parse == 'no'

args.ignorethree = int(args.ignorethree)

assert args.ignorethree >= 0

# func for emit

def remove_tone(pinyin):
    tone_dict = {
        'a': 'a',
        'e': 'e',
        'i': 'i',
        'o': 'o',
        'u': 'u',
        'ü': 'v',
    }
    tone_list = ['ā', 'á', 'ǎ', 'à', 'ē', 'é', 'ě', 'è', 'ī', 'í', 'ǐ', 'ì',
                 'ō', 'ó', 'ǒ', 'ò', 'ū', 'ú', 'ǔ', 'ù', 'ǖ', 'ǘ', 'ǚ', 'ǜ']
    for tone in tone_list:
        if tone in pinyin:
            pinyin = pinyin.replace(tone, tone_dict[tone[0]])
            break
    return pinyin

def convert_to_pinyin(sentence):
    pinyin_list = pypinyin.lazy_pinyin(sentence, style=pypinyin.Style.NORMAL)
    
    pinyin_list = [remove_tone(pinyin) for pinyin in pinyin_list]
    
    return pinyin_list

# get sentence

sentence_list = []

def read_sina_news(corpus_path):
    corpus_list = os.listdir(corpus_path)
    for filename in corpus_list:
        if filename.startswith('.'):
            continue
        if 'README' in filename:
            continue
        file_path = os.path.join(corpus_path, filename)

        if os.path.isfile(file_path):
            with open(file_path, 'r', encoding='gbk') as f:
                for line in f.readlines():
                    line = json.loads(line)
                    text = line['html']
                    if args.parse == 'yes':
                        texts = re.split(r'[。！？，；]', text)
                        for text in texts:
                            filtered_text = re.findall(r'[\u4e00-\u9fa5]+', text)
                            filtered_sentence = ''.join(filtered_text)
                            sentence_list.append(filtered_sentence)
                    else:
                        filtered_text = re.findall(r'[\u4e00-\u9fa5]+', text)
                        filtered_sentence = ''.join(filtered_text)
                        sentence_list.append(filtered_sentence)

def default_read_corpus(corpus_path):
    corpus_list = os.listdir(corpus_path)

    for filename in corpus_list:
        if filename.startswith('.'):
            continue
        if 'README' in filename:
            continue
        file_path = os.path.join(corpus_path, filename)

        if os.path.isfile(file_path):
            with open(file_path, 'r', encoding='gbk') as f:
                for line in f.readlines():
                    # default extract Chinese without json
                    if args.parse == 'yes':
                        texts = re.split(r'[。！？，；]', line)
                        for text in texts:
                            filtered_text = re.findall(r'[\u4e00-\u9fa5]+', text)
                            filtered_sentence = ''.join(filtered_text)
                            sentence_list.append(filtered_sentence)
                    else:
                        filtered_text = re.findall(r'[\u4e00-\u9fa5]+', line)
                        filtered_sentence = ''.join(filtered_text)
                        sentence_list.append(filtered_sentence)

if args.corpus[0] == 'sina':
    corpus_path = '../corpus/sina_news_gbk'
    read_sina_news(corpus_path)

elif args.corpus[0] == 'sina_and_smp':
    corpus_path = '../corpus/sina_news_gbk'
    read_sina_news(corpus_path)

    corpus_path = '../corpus/SMP2020'
    default_read_corpus(corpus_path)

else:
    for cur_corpus in args.corpus:
        corpus_path = '../corpus/' + cur_corpus
        default_read_corpus(corpus_path)

# get prob from sentence

word2count = {}
twowords2count = {}
threewords2count = {}
skip2words2count = {}
word2pinyincount = {}

for sentence in tqdm.tqdm(sentence_list):
    if args.emit == 'yes':
        pinyin_sentence = convert_to_pinyin(sentence)

    for i in range(len(sentence)):
        word = sentence[i]

        if word not in word2count:
            word2count[word] = 1
        else:
            word2count[word] += 1
        
        if i >= 1:
            last_word = sentence[i-1]
            if last_word + ' ' + word not in twowords2count:
                twowords2count[last_word + ' ' + word] = 1
            else:
                twowords2count[last_word + ' ' + word] += 1
        
        if args.three == 'yes':
            if i >= 2:
                last_word = sentence[i-1]
                last_last_word = sentence[i-2]
                if last_last_word + last_word + word not in threewords2count:
                    threewords2count[last_last_word + last_word + word] = 1
                else:
                    threewords2count[last_last_word + last_word + word] += 1
        
        if args.emit == 'yes':
            word_pinyin = pinyin_sentence[i]
            if word not in word2pinyincount:
                word2pinyincount[word] = {word_pinyin: 1}
            else:
                if word_pinyin not in word2pinyincount[word]:
                    word2pinyincount[word][word_pinyin] = 1
                else:
                    word2pinyincount[word][word_pinyin] += 1
        
        if args.skip2 == 'yes':
            if i >= 2:
                last_last_word = sentence[i-2]
                if last_last_word + ' ' + ' ' + ' ' + word not in skip2words2count:
                    skip2words2count[last_last_word + ' ' + ' ' + ' ' + word] = 1
                else:
                    skip2words2count[last_last_word + ' ' + ' ' + ' ' + word] += 1


if args.three == 'yes':
    keys_to_remove = [key for key, value in threewords2count.items() if value < args.ignorethree]

    for key in keys_to_remove:
        del threewords2count[key]

# TODO: draw histograph

# for twowords, count in twowords2count.items():
#     if count < args.ignoretwo:
#         twowords2count.pop(twowords)

if args.corpus[0] == 'sina':
    WORD2COUNT_PATH = '../data/word2count_sina.json'
    TWOWORDS2COUNT_PATH = '../data/twowords2count_sina.json'
    THREEWORDS2COUNT_PATH = '../data/threewords2count_sina.json'
    SKIP2WORDS2COUNT_PATH = '../data/skip2words2count_sina.json'
    WORD2PINYINCOUNT_PATH = '../data/word2pinyincount_sina.json'
    PINYIN2WORD_PATH = '../data/pinyin2word.json'
        
elif args.corpus[0] == 'sina_and_smp':
    WORD2COUNT_PATH = '../data/word2count_sina_and_smp.json'
    TWOWORDS2COUNT_PATH = '../data/twowords2count_sina_and_smp.json'
    THREEWORDS2COUNT_PATH = '../data/threewords2count_sina_and_smp.json'
    SKIP2WORDS2COUNT_PATH = '../data/skip2words2count_sina_and_smp.json'
    WORD2PINYINCOUNT_PATH = '../data/word2pinyincount_sina_and_smp.json'
    PINYIN2WORD_PATH = '../data/pinyin2word.json'

else: 
    WORD2COUNT_PATH = '../data/word2count_my_corpus.json'
    TWOWORDS2COUNT_PATH = '../data/twowords2count_my_corpus.json'
    THREEWORDS2COUNT_PATH = '../data/threewords2count_my_corpus.json'
    SKIP2WORDS2COUNT_PATH = '../data/skip2words2count_my_corpus.json'
    WORD2PINYINCOUNT_PATH = '../data/word2pinyincount_my_corpus.json'
    PINYIN2WORD_PATH = '../data/pinyin2word_my_corpus.json'

if args.parse == 'yes':
    WORD2COUNT_PATH = WORD2COUNT_PATH.replace('.json', '') + '_parse' + '.json'
    TWOWORDS2COUNT_PATH = TWOWORDS2COUNT_PATH.replace('.json', '') + '_parse' + '.json'
    THREEWORDS2COUNT_PATH = THREEWORDS2COUNT_PATH.replace('.json', '') + '_parse' + '.json'
    SKIP2WORDS2COUNT_PATH = SKIP2WORDS2COUNT_PATH.replace('.json', '') + '_parse' + '.json'

with open(WORD2COUNT_PATH, 'w') as f:
    json.dump(word2count, f, indent=4)

with open(TWOWORDS2COUNT_PATH, 'w') as f:
    json.dump(twowords2count, f, indent=4)

if args.three == 'yes':
    with open(THREEWORDS2COUNT_PATH, 'w') as f:
        json.dump(threewords2count, f, indent=4)

if args.emit == 'yes':
    with open(WORD2PINYINCOUNT_PATH, 'w') as f:
        json.dump(word2pinyincount, f, indent=4)

if args.skip2 == 'yes':
    with open(SKIP2WORDS2COUNT_PATH, 'w') as f:
        json.dump(skip2words2count, f, indent=4)

# get pinyin2word

pinyin2word = {}

PINYINHANZI_PATH = '../corpus/' + args.pinyin

with open(PINYINHANZI_PATH, 'r', encoding='gbk') as f:
    for line in f.readlines():
        line = line.strip().split()

        pinyin = line[0]
        words = line[1:]

        pinyin2word[pinyin] = words

with open(PINYIN2WORD_PATH, 'w') as f:
    json.dump(pinyin2word, f, indent=4)

T2 = time.time()

print("time: {:.2f} s".format(T2 - T1))