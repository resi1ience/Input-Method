# PINYIN IME

## 环境配置

需要Python环境，推荐Python>=3.9

需要的Python库：

- tqdm
- pypinyin

## 文件放置

```
.
├── corpus
│   ├── your_corpus1
│   │   ├── 1.txt
│   │   └── ...
│   ├── your_corpus2
│   │   ├── 1.txt
│   │   └── ...
│   └── your_pinyin_hanzi_table.txt
├── data
│   ├── input.txt
│   └── output.txt
└── src
    ├── eval.py
    ├── infer.py
    └── process.py
```

请按照如上方式放置你的文件，其中:

- ``your_corpus{i}``代表你的第i个语料库文件夹，其中应存放着多个txt文件，请确保这些txt文件都是gbk编码的
- ``your_pinyin_hanzi_table.txt``代表你的拼音汉字表
- ``input.txt`` ``output.txt``为你要测试的标准输入输出

your_pinyin_hanzi_table.txt需要有如下格式

```txt
a 啊 嗄 腌 吖 阿 锕
ai 锿 暧 爱 呆 嗌 艾 癌 哎 蔼 皑 砹 隘 碍 矮 埃 挨 捱 嫒 唉 哀 霭 嗳 瑷
...
```

input.txt需要有如下格式

```txt
bei jing shi shou ge ju ban guo xia ao hui yu dong ao hui de cheng shi
ji qi xue xi shi dang xia fei chang huo re de ji shu
...
```

output.txt需要有如下格式

```txt
北京是首个举办过夏奥会与冬奥会的城市
机器学习是当下非常火热的技术
...
```

## 运行

运行分为处理、推理、测试三步：

在开始之前，请先移动到src文件夹

```bash
cd src
```

### 处理（process）

使用process.py进行处理，有以下必须提供的参数：

- -c/--corpus: 代表你的语料库文件夹名，如在文件放置部分提到的your_corpus1，若采用多个语料库，请用空格分隔，如 ``your_corpus1 your_corpus2``
- -py/--pinyin: 代表你的拼音汉字表名，如在文件放置部分提到your_pinyin_hanzi_table.txt

基本格式：

```bash
python process.py -c your_corpus1 your_corpus2 -py your_pinyin_hanzi_table.txt
```

其他可选参数：

- -e/--emit: 是否统计多音字（即在推理时考虑发射概率），可选yes/no，默认为no
- -t/--three: 是否统计三元词（即在推理时考虑三元语法），可选yes/no，默认为no
- -igth/--ignorethree: 在统计三元词时只统计出现次数大于等于x的，x可选任意正整数，默认x为2
- -s/--skip2: 是否统计间隔的二元词（如"x\*y"的个数，x、y分别为被统计汉字，\*为任意汉字），可选yes/no，默认为no，（统计原因详见report）
- -p/--parse: 是否将语料文件中的每行按标点符号分开，可选yes/no，默认为yes

注：对于一些较大的语料库，若不选do parse，可能导致中间文件过大而无法继续推理

实例格式：

```bash
python process.py -c your_corpus1 your_corpus2 -py your_pinyin_hanzi_table.txt -e yes -t yes -igth 2 -s no -p yes
```

在执行完process.py后:

- 会产生推理（infer）所需的数据文件，出现在data目录下
- 会在命令行中打印处理时间，格式例：``time: 316.37 s``

### 推理（infer）

使用infer.py进行处理，有以下必须提供的参数：

- -c/--corpus: 代表你的语料库文件夹名，如在文件放置部分提到的your_corpus1，若采用多个语料库，请用空格分隔，如 ``your_corpus1 your_corpus2``

基本格式（将直接在命令行中键入拼音并得到输出，通过ctrl+D结束输入）：

```bash
python infer.py
```

推荐使用输入输出重定向，如：

```bash
python infer.py < ../data/input.txt > ../data/your_output.txt -c your_corpus1 your_corpus2
```

可选参数：

- -e/--emit: 是否在推理时考虑发射概率，可选yes/no，默认为no
- -t/--three: 是否在推理时考虑三元语法，可选yes/no，默认为no
- -rtt/--ratiothreetwo: 三元语法 占到 全部转移概率 的比例，可选0到1间的数，默认为0.74
- -rto/--ratiotwoone: 二元语法 占到 二元与一元语法之和 的比例，可选0到1间的数，默认为0.99
- -u/--use_extra_p: 是否使用额外的填空概率，需要-t为yes，且需要处理（infer）时-s为yes（填空概率的说明详见report）
- -p/--parse: process时是否将语料文件中的每行按标点符号分开了，可选yes/no，默认为yes

**请注意，推理（infer）时的参数（-e、-t、-u、-p）需要与处理（process）时的参数匹配，如此处指定-t为yes需要处理（process）时也指定-t为yes！**

实例格式：

```bash
python infer.py < ../data/input.txt > ../data/your_output.txt -c your_corpus1 your_corpus2 -e yes -t yes -rtt 0.74 -rto 0.98 -p yes
```

在执行完infer.py后:

- 会产生测试（eval）所需的输出文件，出现在data目录下
- 输出文件最后打印了推理时间，格式例：``time: 44.92 s``

### 测试（eval）

使用eval.py进行处理，有以下必须提供的参数：

- -a/--answer: 答案文件，即在文件放置部分提到的output.txt
- -o/--output: 输出文件，即在推理部分提到的your_output.txt

基本格式：

```bash
python eval.py -a ../data/output.txt -o ../data/your_output.txt
```

执行命令会得到句准确率（sentence acc）和词准确率（word acc），格式例：

```
sentence acc:  0.38922155688622756
word acc:  0.8526591107236269
```
