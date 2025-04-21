import json
import sys
import math
import argparse
import time

T1 = time.time()

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--corpus', help='corpus list', nargs='+', type=str, required=True)
parser.add_argument('-e', '--emit', help='use emit or not', default='no', required=False)
parser.add_argument('-t', '--three', help='use 3-gram or not', default='no', required=False)
parser.add_argument('-rtt', '--ratiothreetwo', help='ratio of three-gram to two-gram', default=0.74, required=False)
parser.add_argument('-rto', '--ratiotwoone', help='ratio of two-gram to one-gram', default=0.99, required=False)
parser.add_argument('-u', '--use_extra_p', help='use mixed three to two prob', default='no', required=False)
parser.add_argument('-p', '--parse', help='parse comma... or not', default='yes', required=False)

args = parser.parse_args()

assert args.emit == 'yes' or args.emit == 'no'
assert args.three == 'yes' or args.three == 'no'
assert args.parse == 'yes' or args.parse == 'no'
assert (args.use_extra_p == 'yes' and args.three == 'yes') or args.use_extra_p == 'no'

args.ratiothreetwo = float(args.ratiothreetwo)
args.ratiotwoone = float(args.ratiotwoone)

assert 0 <= args.ratiothreetwo <= 1
assert 0 <= args.ratiotwoone <= 1

# macros

RARESCORE = 1000000

# read data

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


total_word_count = 0
with open(WORD2COUNT_PATH, "r") as f:
    word2count = json.load(f)
    for key, value in word2count.items():
        total_word_count += value
    # for key, value in word2count.items():
    #     word2count[key] /= total_word_count

with open(TWOWORDS2COUNT_PATH, "r") as f:
    twowords2count = json.load(f)

with open(PINYIN2WORD_PATH, "r") as f:
    pinyin2word = json.load(f)

word2pinyincount = {}
if args.emit == 'yes':
    with open(WORD2PINYINCOUNT_PATH, "r") as f:
        word2pinyincount = json.load(f)
    for key, value in word2pinyincount.items():
        word_pinyin_count_total = 0
        for pinyin, count in value.items():
            word_pinyin_count_total += count
        for pinyin, count in value.items():
            value[pinyin] = count / word_pinyin_count_total

threewords2count = {}
if args.three == 'yes':
    with open(THREEWORDS2COUNT_PATH, "r") as f:
        threewords2count = json.load(f)

skip2words2count = {}
if args.use_extra_p == 'yes':
    with open(SKIP2WORDS2COUNT_PATH, "r") as f:
        skip2words2count = json.load(f)
    ratiointhree = [0.0006, 0.0004, 0.999]

# begin infer

while True:
    input_string = sys.stdin.readline()
    if not input_string:
        break
    input_pinyins = input_string.strip().split()

    dp = [{}]
    path = [{}]

    for i in range(len(input_pinyins)):
        cur_pinyin = input_pinyins[i]

        if i == 0: # first pinyin
            for word in pinyin2word[cur_pinyin]:
                zero_flag = False
                if args.emit == 'yes': # calculate emit prob
                    duoyin_score = 0
                    if word in word2pinyincount:
                        if cur_pinyin in word2pinyincount[word]:
                            duoyin_score = word2pinyincount[word][cur_pinyin]
                        else:
                            zero_flag = True
                    else:
                        zero_flag = True
                
                if word not in word2count:
                    zero_flag = True
                else:
                    cur_singleword_count = word2count[word]

                if zero_flag == True:
                    dp[0][word] = RARESCORE
                else: # 1-gram prob
                    score_before_log = cur_singleword_count / total_word_count
                    if args.emit == 'yes':
                        score_before_log = score_before_log * duoyin_score
                    dp[0][word] = -math.log(score_before_log)

                path[0][word] = -1

            continue

        if i == 1 or (i > 1 and args.three == 'no'): # use two-gram
            last_pinyin = input_pinyins[i-1]
            dp.append({})
            path.append({})

            for word in pinyin2word[cur_pinyin]:
                dp[i][word] = math.inf
                for last_word in pinyin2word[last_pinyin]: # enumerate last word
                    zero_flag = False

                    if last_word + " " + word not in twowords2count:
                        zero_flag = True
                    else:
                        cur_twoword_count = twowords2count[last_word + " " + word]
                    
                    if word not in word2count:
                        zero_flag = True
                    else:
                        cur_singleword_count = word2count[word]

                    if last_word not in word2count:
                        zero_flag = True
                    else:
                        last_singleword_count = word2count[last_word]

                    if args.emit == 'yes': # calculate emit prob
                        duoyin_score = 0
                        if word in word2pinyincount:
                            if cur_pinyin in word2pinyincount[word]:
                                duoyin_score = word2pinyincount[word][cur_pinyin]
                            else:
                                zero_flag = True
                        else:
                            zero_flag = True

                    if zero_flag == True:
                        cur_score = RARESCORE
                    else: # 2-gram prob
                        score_before_log = args.ratiotwoone * cur_twoword_count / last_singleword_count + (1-args.ratiotwoone) * cur_singleword_count / total_word_count

                        if args.emit == 'yes':
                            score_before_log = score_before_log * duoyin_score
                        cur_score = -math.log(score_before_log)

                    if last_word not in dp[i-1]:
                        continue

                    if cur_score + dp[i-1][last_word] < dp[i][word]:
                        dp[i][word] = cur_score + dp[i-1][last_word]
                        path[i][word] = last_word
            continue

        # i >= 2 and use three-gram

        last_pinyin = input_pinyins[i-1]
        last_last_pinyin = input_pinyins[i-2]
        dp.append({})
        path.append({})

        for word in pinyin2word[cur_pinyin]:
            dp[i][word] = math.inf
            for last_word in pinyin2word[last_pinyin]:
                # for last_last_word in pinyin2word[last_last_pinyin]: # enumerate last last word
                    last_last_word = path[i-1][last_word] # don't enumerate last last word

                    use_formula = 3
                    zero_flag = False

                    if last_last_word + last_word + word not in threewords2count:
                        use_formula = 2 # degrade to two-gram
                    else:
                        cur_threeword_count = threewords2count[last_last_word + last_word + word]
                    
                    if last_last_word + " " + last_word not in twowords2count:
                        use_formula = 2 # degrade to two-gram
                    else:
                        last_twoword_count = twowords2count[last_last_word + " " + last_word]

                    if args.use_extra_p == 'yes':
                        if last_last_word + '   ' + word not in skip2words2count:
                            use_formula = 2
                        else:
                            cur_skip2word_count = skip2words2count[last_last_word + '   ' + word]

                    if last_word + " " + word not in twowords2count:
                        zero_flag = True
                    else:
                        cur_twoword_count = twowords2count[last_word + " " + word]

                    if last_word not in word2count:
                        zero_flag = True
                    else:
                        last_singleword_count = word2count[last_word]

                    if word not in word2count:
                        zero_flag = True
                    else:
                        cur_singleword_count = word2count[word]

                    if args.emit == 'yes': # calculate emit prob
                        duoyin_score = 0
                        if word in word2pinyincount:
                            if cur_pinyin in word2pinyincount[word]:
                                duoyin_score = word2pinyincount[word][cur_pinyin]
                            else:
                                zero_flag = True
                        else:
                            zero_flag = True
                    
                    if zero_flag == True:
                        cur_score = RARESCORE
                    else:
                        if args.use_extra_p == 'yes': # use mixed three to two prob
                            if use_formula == 3:
                                score_before_log = args.ratiothreetwo * (ratiointhree[2] * cur_threeword_count / last_twoword_count + ratiointhree[1] * cur_threeword_count / cur_skip2word_count + ratiointhree[0] * cur_threeword_count / cur_twoword_count) + (1-args.ratiothreetwo) * (args.ratiotwoone * cur_twoword_count / last_singleword_count + (1-args.ratiotwoone) * cur_singleword_count / total_word_count)
                            elif use_formula == 2:
                                score_before_log = args.ratiotwoone * cur_twoword_count / last_singleword_count + (1-args.ratiotwoone) * cur_singleword_count / total_word_count
                            else:
                                score_before_log = cur_singleword_count / total_word_count
                        else:
                            if use_formula == 3: # 3-gram prob
                                score_before_log = args.ratiothreetwo * (cur_threeword_count / last_twoword_count) + (1-args.ratiothreetwo) * (args.ratiotwoone * cur_twoword_count / last_singleword_count + (1-args.ratiotwoone) * cur_singleword_count / total_word_count)
                            elif use_formula == 2: # degrade to two-gram
                                score_before_log = args.ratiotwoone * cur_twoword_count / last_singleword_count + (1-args.ratiotwoone) * cur_singleword_count / total_word_count
                            else:
                                score_before_log = cur_singleword_count / total_word_count
                        
                        if args.emit == 'yes':
                            score_before_log = score_before_log * duoyin_score
                        
                        cur_score = -math.log(score_before_log)

                    if last_word not in dp[i-1]:
                        continue

                    if cur_score + dp[i-1][last_word] < dp[i][word]:
                        dp[i][word] = cur_score + dp[i-1][last_word]
                        path[i][word] = last_word

    final_dp = dp[-1]
    final_words = ''
    min_score = math.inf
    for key, value in final_dp.items(): # find the min score
        if value < min_score:
            min_score = value
            final_words = key
    
    final_ans = ''

    for i in range(len(input_pinyins)-1, -1, -1): # find the path
        final_ans += final_words
        final_words = path[i][final_words]
    
    final_ans = final_ans[::-1] # reverse the path

    print(final_ans)

T2 = time.time()

print("time: {:.2f} s".format(T2 - T1))