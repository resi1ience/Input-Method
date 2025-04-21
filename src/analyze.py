import argparse

parser = argparse.ArgumentParser()

parser.add_argument('-a', '--answer', help='answer file name', required=True)
parser.add_argument('-o', '--output', help='output file name', required=True)

args = parser.parse_args()

answer_path = args.answer

answer_list = []

with open(answer_path, 'r') as f:
    for line in f.readlines():
        answer_list.append(line)

output_path = args.output

output_list = []

with open(output_path, 'r') as f:
    for line in f.readlines():
        output_list.append(line)

total_word_count = 0
total_sentence_count = len(answer_list)

correct_word_count = 0
correct_sentence_count = 0

right_sentence_list = []
wrong_sentence_list = []

for i in range(len(output_list)):
    output_sentence = output_list[i]
    if output_sentence.startswith('time'):
        break
    answer_sentence = answer_list[i]

    total_word_count += len(answer_sentence)

    for j in range(len(output_sentence)):
        if j >= len(answer_sentence):
            break

        if output_sentence[j] == answer_sentence[j]:
            correct_word_count += 1
    
    if answer_sentence == output_sentence:
        correct_sentence_count += 1
        right_sentence_list.append(output_sentence)
    
    else:
        wrong_sentence_list.append((answer_sentence, output_sentence))

print("sentence acc: ", correct_sentence_count / total_sentence_count)
print("word acc: ", correct_word_count / total_word_count)

right_sentence_list = sorted(right_sentence_list, reverse=True, key=lambda x:len(x))

print("right: ")

print(right_sentence_list[:5])

wrong_sentence_list = sorted(wrong_sentence_list, reverse=True, key=lambda x:len(x[0]))

print("wrong: ")

print(wrong_sentence_list[:5])