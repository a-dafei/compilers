# compilers
一个python语言写的编译器，实现了词法分析和语法分析。


此工程共有两个部分：词法分析部分和语法分析部分。
1.词法分析部分共有5个文件：
Grammar1.txt -- 正规文法
source1.cpp -- 源程序1，用此程序检验词法分析，检测标识符常量等正确与否
source2.cpp -- 源程序2，此程序各个常量标识符等皆正确，供后面程序分析
LexAnalysis.py -- 词法分析文件，输出分析结果，并生成token_table.data文件
token_table.data -- token表
2.语法分析部分共有4个文件：
Grammar2.txt -- 2型文法
token_table.data -- 词法分析输出的token表，用来进行语法分析
SynAnalysis.py -- 语法分析文件，输出分析结果，并生成Action_and_Goto.data文件
Action_and_Goto.data -- action 和 goto 表
3.两个可执行文件：
LexAnalysis.exe
SynAnalysis.exe


