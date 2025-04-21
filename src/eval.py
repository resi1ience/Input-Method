import argparse
# import nltk
# from nltk.translate.bleu_score import sentence_bleu
# from rouge import Rouge

parser = argparse.ArgumentParser()

parser.add_argument('-a', '--answer', help='answer file name', required=True)
parser.add_argument('-o', '--output', help='output file name', required=True)
# parser.add_argument('-b', '--bleu', help='calculate bleu or not', default='no', required=False)
# parser.add_argument('-r', '--rouge', help='calculate rouge or not', default='no', required=False)

args = parser.parse_args()

answer_path = args.answer

# assert args.bleu == 'yes' or args.bleu == 'no'
# assert args.rouge == 'yes' or args.rouge == 'no'

# def calculate_bleu(answer_sentence, output_sentence):
#     reference = [answer_sentence.split()]
#     candidate = output_sentence.split()

#     def my_smoothie(precision, **kwargs):
#         if precision == 0:
#             return 0.1
#         else:
#             return precision

#     bleu_score = sentence_bleu(reference, candidate, smoothing_function=my_smoothie)
#     return bleu_score

# def calculate_rouge(answer_sentence, output_sentence):
#     rouge = Rouge()
#     scores = rouge.get_scores(output_sentence, answer_sentence)
#     rouge_n_score = scores[0]['rouge-1']['f']
#     rouge_l_score = scores[0]['rouge-l']['f']
#     return rouge_n_score, rouge_l_score

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

# bleu_total = 0
# rouge_n_total = 0
# rouge_l_total = 0

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
    
    # if args.bleu == 'yes':
    #     bleu = calculate_bleu(answer_sentence, output_sentence)
    #     bleu_total += bleu
    
    # if args.rouge == 'yes':
    #     rouge_n, rouge_l = calculate_rouge(answer_sentence, output_sentence)
    #     rouge_n_total += rouge_n
    #     rouge_l_total += rouge_l

print("sentence acc: ", correct_sentence_count / total_sentence_count)
print("word acc: ", correct_word_count / total_word_count)

# if args.bleu == 'yes':
#     print('BLEU average: ', bleu_total / total_sentence_count)
    
# if args.rouge == 'yes':
#     print('ROUGE-N average: ', rouge_n_total / total_sentence_count)
#     print('ROUGE-L average: ', rouge_l_total / total_sentence_count)