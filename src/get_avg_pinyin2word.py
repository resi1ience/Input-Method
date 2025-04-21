import json
PINYIN2WORD_PATH = '../data/pinyin2word.json'

with open(PINYIN2WORD_PATH, "r") as f:
    pinyin2word = json.load(f)

total_len = 0
key_num = 0

for key, value in pinyin2word.items():
    total_len += len(value)
    key_num += 1

print(total_len / key_num)

total_len = 0
key_num = 0

with open('../test/std_input.txt', 'r') as f:
    for line in f.readlines():
        pinyins = line.split()
        total_len += len(pinyins)
        key_num += 1

    print(total_len / key_num)