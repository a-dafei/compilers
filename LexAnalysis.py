import os

digit = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u',
            'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P',
            'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
symbol = [',', ';', '(', ')', '[', ']', '{', '}', '+', '-', '*', '/', '%', '^', '&', '=', '~', '<', '>']
keyword = ['int', 'double', 'char', 'float', 'delete', 'void', 'break', 'continue', 'do', 'while', 'for', 'if', 'else',
           'abstract', 'return', 'long', 'class', 'scanf', 'print', 'function']


class NFANode(object):
    # Name: 节点的名称
    # isFinal: 此节点是否为终态节点
    # Edge: 边，以字典形式存储，键值对对应输入和下一节点
    def __init__(self, Name=None, isFinal=0):
        super(NFANode, self).__init__()
        self.Name = Name
        self.isFinal = isFinal
        self.Edge = {}

    def addEdge(self, cin_ci, next_ci):
        if cin_ci not in self.Edge:
            nextNodes = set()  # 创建集合
            nextNodes.add(next_ci)
            self.Edge[cin_ci] = nextNodes  # 输入alpha对应的节点名字
        else:
            self.Edge[cin_ci].add(next_ci)


class NFA(object):
    # terminators 终结符的集合
    # status 所有节点的集合，以字典形式存储
    def __init__(self, terminators=None):
        super(NFA, self).__init__()
        self.terminators = terminators
        self.status = {}


class DFANode(object):

    def __init__(self, Name=None, isFinal=0):
        super(DFANode, self).__init__()
        self.Name = Name
        self.isFinal = isFinal
        self.Edge = {}

    def addEdge(self, cin_ci, next_ci):
        if cin_ci not in self.Edge:
            nextNodes = set()
            nextNodes.add(next_ci)
            self.Edge[cin_ci] = nextNodes
        else:
            self.Edge[cin_ci].add(next_ci)


class DFA(object):

    def __init__(self, terminators=None):
        super(DFA, self).__init__()
        self.terminators = terminators
        self.status = {}


class LexAnalysis(object):

    def __init__(self):
        super(LexAnalysis, self).__init__()
        self.productions = []
        self.alphabets = {}
        self.keywords = {}
        self.NFA = None
        self.DFA = None
        self.alphabets['alphabet'] = set(alphabet)
        self.alphabets['digit'] = set(digit)
        self.alphabets['symbol'] = set(symbol)
        for word in keyword:
            self.keywords[word] = 'keyword'

    def ReadLexGrammar(self, filename):
        Lcurrent = None
        Rcurrent = []
        line_num = 0
        # 逐行读取正规文法
        for line in open(filename, 'r'):
            line = line.split('\n')[0]
            # 找到用:代表的->
            i = line.find(':')
            Lcurrent = line[0:i]                 # 产生式左边
            Rcurrent = line[i + 1:len(line)]     # 产生式右边
            line_num += 1
            production = {}
            production['left'] = Lcurrent
            # 找空格，判断产生式右边是否有非终结符
            j = Rcurrent.find(' ')
            # 右边有非终结符 A—>aB
            if j != -1:
                production['input'] = Rcurrent[0:j]
                production['right'] = Rcurrent[j+1:len(Rcurrent)]
            # 右边没有非终结符  A->a
            else:
                production['input'] = Rcurrent
                production['right'] = None
            self.productions.append(production)

    def createNFA(self):
        Status = {}

        def getNFANode(Name, isFinal):
            if Name in Status:
                node = Status[Name]
            else:
                node = NFANode(Name=Name, isFinal=isFinal)
            return node
        start_node = getNFANode('start', 0)
        end_node = getNFANode('end', 1)
        Status['start'] = start_node
        Status['end'] = end_node
        for pro in self.productions:
            now_ci = pro['left']
            cin_ci = pro['input']
            next_ci = pro['right']
            # 对每个产生式，先创建左边节点
            now_node = getNFANode(now_ci, 0)
            # 如果右边有非终结符，指向对应节点，即产生式为 A—>aB型，对B创建节点
            if next_ci is not None:
                next_node = getNFANode(next_ci, 0)
            #  输入字符不是由数字，字母表示成的终结符，即自身是一个终结符
            if cin_ci not in self.alphabets.keys():
                if next_ci is None:
                    now_node.addEdge(cin_ci, 'end')
                else:
                    if next_ci in self.alphabets.keys():
                       for val in self.alphabets[next_ci]:
                        now_node.addEdge(cin_ci, val)
                    else:
                        now_node.addEdge(cin_ci, next_ci)
            # 输入字符是由数字，字母表示的终结符
            else:
                for val in self.alphabets[cin_ci]:
                    if next_ci is None:
                        now_node.addEdge(val, 'end')
                    else:
                        if next_ci in self.alphabets.keys():
                            for tval in self.tool_set[next_ci]:
                                 now_node.addEdge(val, tval)
                        else:
                                 now_node.addEdge(val, next_ci)
            # 更新NFA中的全部节点
            Status[now_ci] = now_node
            if next_ci is not None:
                Status[next_ci] = next_node
        # NFA的终结符集合的元素值的ASCII值为 32 - 126
        terminators = set()
        for i in range(ord(' '), ord('~') + 1):
            terminators.add(chr(i))
        self.NFA = NFA(terminators)
        self.NFA.status = Status

    def createDFA(self):
        Status = {}

        def getDFANode(Name, isFinal):
            if Name in Status:
                return Status[Name]
            else:
                node = DFANode(Name, isFinal)
            return node
        # 求$对应的节点名字
        for node_name in self.NFA.status['start'].Edge['$']:
            start_node = getDFANode('start', 0)
            dfa_node = getDFANode(node_name, 0)
            start_node.addEdge('$', node_name)
            Status['start'] = start_node
            Status[node_name] = dfa_node
            # 记录DFA节点是否已经访问过
            FINvisit = set()
            queue = list()
            # 最初的NFA节点集合，即DFA节点
            nfa_node_set = set()
            nfa_node_set.add(node_name)
            queue.append((nfa_node_set, node_name))
            #  子集法
            while queue:
                node_name = queue.pop(0)   # 从queue中清除队首并返回
                now_node_set = node_name[0]
                now_node_name = node_name[1]
                now_dfa_node = getDFANode(now_node_name, 0)
                # move(I,cin_ci)  寻找后续状态
                for cin_ci in self.NFA.terminators:
                    # 下一节点的NFA集合,move(I,cin_ci)
                    next_set = set()
                    for nfa_node_name in now_node_set:
                        nfa_node = self.NFA.status[nfa_node_name]
                        # 有出边
                        if cin_ci in nfa_node.Edge.keys():
                            for name in nfa_node.Edge[cin_ci]:
                                next_set.add(name)  # 存 move(I,cin_ci)
                    # 如果next_set为空，则直接返回
                    if not next_set:
                        continue
                    next_node_name = ''
                    isFinal = 0
                    temp_list = list(next_set)
                    next_list = sorted(temp_list)
                    for i in next_list:
                        # NFA集合（DFA节点）命名，若NFA集合有，{a,b,c,d} 则DFA节点命名为字符串‘a,b,c,d’
                        next_node_name = '%s$%s' % (next_node_name, i)
                        isFinal += int(self.NFA.status[i].isFinal)
                    # 如果集合中有一个NFA的终态，该节点就是DFA的终态
                    if isFinal > 0:
                        isFinal = 1
                    next_dfa_node = getDFANode(next_node_name, isFinal)
                    now_dfa_node.addEdge(cin_ci, next_node_name)
                    Status[now_node_name] = now_dfa_node
                    Status[next_node_name] = next_dfa_node
                    # 如果该状态已经访问过，则继续
                    if next_node_name in FINvisit:
                        continue
                    # 如果该状态未访问过，则放入队列中
                    else:
                        FINvisit.add(next_node_name)
                        queue.append((next_set, next_node_name))
        # DFA的终结符集合的元素值的ASCII值为 32 - 126
        terminators = set()
        for i in range(ord(' '), ord('~') + 1):
            terminators.add(chr(i))
        self.DFA = DFA(terminators)
        self.DFA.status = Status

    def runOnDFA(self, line, pos):
        #  若第一个字符为字母或‘_’  则判断其是关键词还是标识符
        if line[pos] in self.alphabets['alphabet'] or line[pos] == '_':
            temp_pos = pos
            temp_str = ''
            while temp_pos < len(line) and line[temp_pos] not in self.alphabets['symbol'] and line[temp_pos] != ' ':
                temp_str += line[temp_pos]
                temp_pos += 1
            Curpos = 0
            token = ''  # 单词
            now_node = self.DFA.status['identifier']
            # 循环刚才截取的单词的字母，如果字母在‘indentifer’的输入中，则进行如下
            while Curpos < len(temp_str) and temp_str[Curpos] in now_node.Edge.keys():
                token += temp_str[Curpos]
                now_node = self.DFA.status[list(now_node.Edge[temp_str[Curpos]])[0]]
                Curpos += 1
            # 单词合法
            if Curpos >= len(temp_str) and now_node.isFinal > 0:
                if token in self.keywords.keys():
                    token_type = self.keywords[token]
                else:
                    token_type = 'identifier'
                return temp_pos - 1, token_type, token, '合法'
            #  单词不合法
            else:
                return temp_pos - 1, None, '', '标识符不合法'
        #  若第一个字符是数字，判断是否是整数，复数，科学计数法以及是否合法
        elif line[pos] in self.alphabets['digit']:
            # 判断是否为复数
            temp_pos = pos
            temp_str = ''
            while temp_pos < len(line) and (line[temp_pos] not in self.alphabets['symbol'] or line[temp_pos] == '+'
                                             or line[temp_pos] == '-') and line[temp_pos] != ' ':
                temp_str += line[temp_pos]
                temp_pos += 1
            Curpos = 0
            token = ''
            now_node = self.DFA.status['complex']
            while Curpos < len(temp_str) and temp_str[Curpos] in now_node.Edge.keys():
                token += temp_str[Curpos]
                now_node = self.DFA.status[list(now_node.Edge[temp_str[Curpos]])[0]]
                Curpos += 1
            if Curpos >= len(temp_str) and now_node.isFinal > 0 and ((len(temp_str)==1 and token[0]>='0') or (len(temp_str) > 1 and (token[1]=='.' or token[0] > '0') )) :
                token_type = 'constant'
                return temp_pos - 1, token_type, token, '合法'
            # 判断是否为科学计数形式常量
            temp_pos = pos
            temp_str = ''
            while temp_pos < len(line) and (line[temp_pos] not in self.alphabets['symbol'] or line[temp_pos] == '+'
                                             or line[temp_pos] == '-') and line[temp_pos] != ' ':
                temp_str += line[temp_pos]
                temp_pos += 1
            Curpos = 0
            token = ''
            now_node = self.DFA.status['scientific']
            while Curpos < len(temp_str) and temp_str[Curpos] in now_node.Edge.keys():
                token += temp_str[Curpos]
                now_node = self.DFA.status[list(now_node.Edge[temp_str[Curpos]])[0]]
                Curpos += 1
            if Curpos >= len(temp_str) and now_node.isFinal > 0 and ((len(temp_str)==1 and token[0]>='0') or (len(temp_str) > 1 and (token[1]=='.' or token[0] > '0') )):
                token_type = 'constant'
                return temp_pos - 1, token_type, token, '合法'
            # 判断是否为整型常量
            temp_pos = pos
            temp_str = ''
            while temp_pos < len(line) and line[temp_pos] not in self.alphabets['symbol'] and line[temp_pos] != ' ':
                temp_str += line[temp_pos]
                temp_pos += 1
            Curpos = 0
            token = ''
            now_node = self.DFA.status['integer']
            while Curpos < len(temp_str) and temp_str[Curpos] in now_node.Edge.keys():
                token += temp_str[Curpos]
                now_node = self.DFA.status[list(now_node.Edge[temp_str[Curpos]])[0]]
                Curpos += 1
            if Curpos >= len(temp_str) and now_node.isFinal > 0 and ((len(temp_str)==1 and token[0]>='0') or (len(temp_str) > 1 and (token[1]=='.' or token[0] > '0') )):
                token_type = 'constant'
                return temp_pos - 1, token_type, token, '合法'
            return temp_pos - 1, None, '', '标识符或常量不合法'
        else:
            # 判断是否为限定符
            Curpos = pos
            token = ''
            token_type = 'limit_symbol'
            now_node = self.DFA.status['limit_symbol']
            # 逐个向后读取字符，并进行状态转移
            while Curpos < len(line) and line[Curpos ] in now_node.Edge.keys():
                token += line[Curpos ]
                now_node = self.DFA.status[list(now_node.Edge[line[Curpos ]])[0]]
                Curpos += 1
            # 如果到达终态，则获得一个单词
            if now_node.isFinal > 0:
                return Curpos - 1, token_type, token, '合法'
            # 判断操作符
            Curpos = pos
            token = ''
            token_type = 'operation'
            now_node = self.DFA.status['operation']
            # 逐个向后读取字符，并进行状态转移
            while Curpos  < len(line) and line[Curpos ] in now_node.Edge.keys():
                token += line[Curpos ]
                now_node = self.DFA.status[list(now_node.Edge[line[Curpos ]])[0]]
                Curpos += 1
            # 如果到达终态，则获得一个单词
            if now_node.isFinal > 0:
                return Curpos - 1, token_type, token, '合法'
            # 其他的未知错误
            Curpos  = pos
            while Curpos < len(line) and line[Curpos] not in self.alphabets['symbol'] \
                    and line[Curpos] not in self.alphabets['digit'] and line[Curpos] not in self.alphabets['alphabet'] \
                    and line[Curpos] != '_' and line[Curpos] != ' ':
                Curpos += 1
            return Curpos - 1, None, '', '未知错误'

    def analysis(self, filename):
        line_num = 0
        is_error = False
        token_table = []
        for line in open(filename, 'r'):
            pos = 0
            line_num += 1
            line = line.split('\n')[0]
            while pos < len(line):
                # 跳过tab，回车，换行，空格
                while pos < len(line) and line[pos] in ['\t', '\n', ' ', '\r']:
                    pos += 1
                if pos < len(line):
                    pos, token_type, token, message = self.runOnDFA(line, pos)
                    if token_type is None:
                        print('词法分析错误： 行 %s, 列 %s : %s' % (str(line_num), str(pos), message))
                        is_error = True
                    else:
                        token_table.append((line_num, token_type, token))
                        print('(%d , %s , %s)' % (line_num, token_type, token))
                    pos += 1
        # 如果分析全部无误，那么写入token表文件
        if not is_error:
            output = open('token_table.data', 'w+')
            for line_num, token_type, token in token_table:
                output.write('( %d %s %s )\n' % (line_num, token_type, token))
            output.close()
            return True
        return False


if __name__ == '__main__':
    lex_ana = LexAnalysis()
    lex_ana.ReadLexGrammar('Grammar1.txt')
    lex_ana.createNFA()
    lex_ana.createDFA()
    lex_ana.analysis('source2.cpp')
    os.system("pause")
