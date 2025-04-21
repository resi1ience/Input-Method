# Pinyin Input Method

This repository contains the implementation of a Pinyin Input Method Editor (IME) based on N-gram models and the Viterbi algorithm.

## Overview

The project aims to convert Pinyin input sequences into the most likely sequence of Chinese characters. It explores character-level Bigram and Trigram language models built from text corpora.

## Models Implemented

1. **Bigram Model:**

   * Uses Viterbi algorithm with transition probabilities based on P(wᵢ | wᵢ₋₁).
   * Employs linear interpolation smoothing with unigram probabilities.
   * Achieved ~38.7% sentence accuracy and ~85.3% word accuracy on the test set using the Sina corpus (baseline).
2. **Trigram Model:**

   * Uses Viterbi with transition probabilities based on P(wᵢ | wᵢ₋₂, wᵢ₋₁).
   * Uses linear interpolation smoothing with Bigram and Unigram probabilities.
   * Includes optimizations like degrading to lower-order n-grams when counts are zero and avoiding full enumeration of wᵢ₋₂ for efficiency.
   * Incorporates optional enhancements:
     * Using a combined Sina News + Weibo (SMP) corpus for better coverage of different language styles.
     * Handling polyphones using `pypinyin` to calculate emission probabilities (`-e yes`).
   * Achieved up to ~62.5% sentence accuracy and ~91.6% word accuracy with enhancements and optimal hyperparameters.
3. **Enhanced Trigram Model (Experimental):**

   * Explores incorporating "filling probabilities" (e.g., P(wᵢ | wᵢ₋₂, wᵢ), requires `-s yes` during processing and `-u yes` during inference) into the trigram scoring.
   * Showed a slight further improvement to ~62.9% sentence accuracy and ~91.8% word accuracy.

*For detailed analysis, model derivation, and performance tuning, please refer to `Report.md` or `Report.pdf` (in Chinese).*

## Requirements

* Python >= 3.9
* Required Python libraries:
  * `tqdm`
  * `pypinyin`

You can install them using pip:

```
pip install tqdm pypinyin
```

## File Structure

Please arrange your files as follows:
.
├── corpus                     # Directory containing your corpora and pinyin table
│   ├── your_corpus1           # Your first corpus directory
│   │   ├── 1.txt
│   │   └── ...
│   ├── your_corpus2           # Your second corpus directory (optional)
│   │   ├── 1.txt
│   │   └── ...
│   └── your_pinyin_hanzi_table.txt # Your Pinyin-to-Hanzi mapping file
├── data                       # Directory for input/output test files
│   ├── input.txt              # Standard input file for testing
│   └── output.txt             # Standard output (ground truth) file for testing
└── src                        # Source code directory
    ├── eval.py                # Evaluation script
    ├── infer.py               # Inference script
    └── process.py             # Preprocessing script

**Notes:**

- your_corpus{i} represents your i-th corpus folder, containing multiple .txt files. Ensure these text files are encoded in GBK.
- your_pinyin_hanzi_table.txt is your Pinyin-to-Hanzi mapping file.
- input.txt and output.txt are your standard test input and expected output files.

**your_pinyin_hanzi_table.txt Format:**

Each line should contain a pinyin followed by space-separated corresponding Hanzi characters.

```
a 啊 嗄 腌 吖 阿 锕
ai 锿 暧 爱 呆 嗌 艾 癌 哎 蔼 皑 砹 隘 碍 矮 埃 挨 捱 嫒 唉 哀 霭 嗳 瑷
```

**input.txt Format:**

Each line contains a sequence of space-separated pinyin syllables.

```
bei jing shi shou ge ju ban guo xia ao hui yu dong ao hui de cheng shi
ji qi xue xi shi dang xia fei chang huo re de ji shu
```

**output.txt Format:**

Each line contains the corresponding ground truth Hanzi sentence.

```
北京是首个举办过夏奥会与冬奥会的城市
机器学习是当下非常火热的技术
```

## Usage

The workflow consists of three steps: Processing, Inference, and Evaluation.
First, navigate to the src directory:

```
cd src
```

1. Processing (process.py)
   This script preprocesses the corpus and builds the necessary n-gram count files.

**Required Arguments:**

- -c/--corpus: Specifies the corpus folder name(s) located in the ../corpus/ directory (e.g., your_corpus1). Use spaces to separate multiple corpus names (e.g., your_corpus1 your_corpus2).
- -py/--pinyin: Specifies the Pinyin-Hanzi table filename located in the ../corpus/ directory (e.g., your_pinyin_hanzi_table.txt).

**Basic Command:**

```
python process.py -c your_corpus1 your_corpus2 -py your_pinyin_hanzi_table.txt
```

**Optional Arguments:**

- -e/--emit: Whether to calculate polyphone statistics (for emission probability during inference). Options: yes/no. Default: no.
- -t/--three: Whether to calculate trigram statistics (for trigram model during inference). Options: yes/no. Default: no.
- -igth/--ignorethree: When counting trigrams (-t yes), only store those appearing >= x times. x can be any positive integer. Default: 2.
- -s/--skip2: Whether to calculate statistics for skipped bigrams (e.g., count of "x * y", where * is any character). Needed for the experimental "filling probability" model (-u yes in inference). Options: yes/no. Default: no. (See report for details).
- -p/--parse: Whether to split lines in corpus files into sentences based on punctuation. Options: yes/no. Default: yes.

**Note:** For very large corpora, not using -p yes (i.e., -p no) might lead to excessively large intermediate files.

**Example Command:**

```
python process.py -c your_corpus1 your_corpus2 -py your_pinyin_hanzi_table.txt -e yes -t yes -igth 2 -s no -p yes
```

**Output:**

- Generates data files (.pkl) required for inference in the ../data/ directory, named based on the corpus names and options used.
- Prints the processing time to the console, e.g., time: 316.37 s.

2. Inference (infer.py)

This script takes Pinyin input and generates the corresponding Hanzi sentences using the preprocessed data.

**Required Arguments:**

- -c/--corpus: Specifies the same corpus folder name(s) used during processing. This helps locate the correct preprocessed data files.

**Basic Usage (Interactive):**

Type Pinyin sequences directly into the console, press Enter after each sequence, and use Ctrl+D (or Ctrl+Z then Enter on Windows) to finish.

```
python infer.py -c your_corpus1 your_corpus2
```

**Recommended Usage (File I/O):**

Use input/output redirection for batch processing.

```
python infer.py -c your_corpus1 your_corpus2 < ../data/input.txt > ../data/your_output.txt
```

**Optional Arguments:**

- -e/--emit: Whether to use emission probabilities (polyphone handling) during inference. Options: yes/no. Default: no. Must match the -e setting used during processing.
- -t/--three: Whether to use the trigram model during inference. Options: yes/no. Default: no. Must match the -t setting used during processing.
- -rtt/--ratiothreetwo: Weight ratio (λ₃) for the trigram probability component in the smoothed score. Only effective if -t yes. Value between 0 and 1. Default: 0.74.
- -rto/--ratiotwoone: Weight ratio (λ₂) for the bigram probability component in the smoothed score (used in both trigram and bigram smoothing). Value between 0 and 1. Default: 0.98 (Note: Original README default was 0.99, but 0.98 might be from optimal settings).
- -u/--use_extra_p: Whether to use the experimental "filling probability". Requires -t yes during inference AND requires -s yes during processing. Default: no. (See report for details).
- -p/--parse: Whether the corpus was parsed into sentences during processing. Options: yes/no. Default: yes. Must match the -p setting used during processing.

**Important Note:** The inference parameters (-e, -t, -u, -p) MUST match the corresponding parameters used during the process.py step for the script to find and use the correct data files and apply the intended model logic!

**Example Command:**

```
python infer.py -c your_corpus1 your_corpus2 -e yes -t yes -rtt 0.74 -rto 0.98 -p yes < ../data/input.txt > ../data/your_output.txt
```

**Output:**

- Generates the output Hanzi sentences file (e.g., ../data/your_output.txt).
- Appends the total inference time to the end of the output file, e.g., time: 44.92 s.

3. Evaluation (eval.py)

This script compares the generated output with the ground truth and calculates accuracy metrics.

**Required Arguments:**

- -a/--answer: Path to the ground truth answer file (e.g., ../data/output.txt).
- -o/--output: Path to the output file generated by infer.py (e.g., ../data/your_output.txt).

**Basic Command:**

```
python eval.py -a ../data/output.txt -o ../data/your_output.txt
```

**Output:**

Prints the sentence accuracy and word accuracy to the console, e.g.:

```
sentence acc:  0.6251497005988024
word acc:  0.9161585550252764
```

## Conclusion

The Trigram model significantly outperforms the Bigram model. Further improvements can be gained by using a combined corpus, handling polyphones (-e yes), careful hyperparameter tuning (e.g., -rtt, -rto), and potentially the experimental "filling probability" (-s yes during processing, -u yes during inference). Choose the model complexity and options based on the desired balance between accuracy and processing/inference time.
