import os


class LRDFANode(object):
    # id 项目集的编号，唯一标识符
    # itemsets 项目集包含项目的集合，每个项目元素以元组形式存储
    def __init__(self, id):
        super(LRDFANode, self).__init__()
        self.id = id
        self.itemsets = set()

    def addItemsets(self, itemset):
        self.itemsets |= itemset


class SynAnalysis(object):
    # 以字典形式存储终结符和非终结符的FirstVt集合
    # 产生式以列表形式存储
    # 终结符和非终结符皆以集合形式存储
    # 产生式集合按照左侧的非终结符归类成新集合，再以字典形式存储
    # 以字典形式存储LR（1）的分析表
    def __init__(self):
        super(SynAnalysis, self).__init__()
        self.FirstVt = {}
        self.productions = []
        self.terminators = set()
        self.NotTerminators = set()
        self.productionsVT = {}
        self.LRTable = {}

    def ReadSynGrammar(self, filename):
        for line in open(filename):
            line = line[:-1]
            Curleft = line.split(':')[0]
            Curright = line.split(':')[1]
            # 若右边产生式有至少两个部分 则将各部分存入一个列表中
            Rlist = []
            #  产生式右侧有多个元素
            if Curright.find(' ') != -1:
                Rlist = Curright.split(' ')
            else:
                Rlist.append(Curright)
            # 以左边产生式作为key 右边产生式作为value 字典形式存储每一行的产生式
            production = {Curleft: Rlist}
            self.productions.append(production)

    def initTerminatorsAndNot(self):
        termSet = set()
        for pro in self.productions:
            for left in pro.keys():
                if left not in self.productionsVT:
                    self.productionsVT[left] = []
                self.productionsVT[left].append((tuple(pro[left]), self.productions.index(pro)))
                termSet.add(left)
                self.NotTerminators.add(left)
                for right in pro[left]:
                    termSet.add(right)
        # 终结符集合 = 全部元素 - 非终结符集合
        self.terminators = termSet-self.NotTerminators

    def getFirstVt(self, Cur, isfangwen):
        # 如果已知当前的FirstVt集 则直接返回
        if Cur in self.FirstVt.keys():
            return self.FirstVt[Cur]
        tempset = set()
        # 如果当前符号是终结符 则其FirstVt集就是其本身
        if Cur in self.terminators:
            tempset.add(Cur)
            return tempset
        # 如果当前符号是非终结符 则往下计算
        isfangwen.add(Cur)
        # 对左边为该非终结符的所有产生式进行计算    X-> Y1 Y2 ... Yn
        for Rlist in self.productionsVT[Cur]:
            flag = True
            for right in Rlist[0]:
                if right == '$':
                    tempset.add('$')
                    break
                # 如果该元素在递归过程中已经访问过，则不再计算
                if right in isfangwen:
                    continue
                cur_set = self.getFirstVt(right, isfangwen)  # 递归求解
                if '$' in cur_set:
                    tempset |= cur_set
                    tempset.remove('$')   # first(Yi)-{$} 并入first集
                else:
                    tempset |= cur_set
                    flag = False
                    # 不含空则不必再计算右边的字符的first集
                    break
            if flag:
                tempset.add('$')
        return tempset

    def GetFirstVt(self):
        for terminator in self.terminators:
            self.FirstVt[terminator] = self.getFirstVt(terminator, set())
        for NotTerminator in self.NotTerminators:
            self.FirstVt[NotTerminator] = self.getFirstVt(NotTerminator, set())

    #  构造LR(1)项目集的闭包函数
    def getCLOSURE(self, Curiterm, CLOitem):
        # 当前项目以元组形式存储过来，依次存有此产生式在产生式编号，左边非终结符，右边产生式集合，点的位置，向前搜索符集合
        CLOitem.add(Curiterm)
        Rlist = Curiterm[2]
        point = Curiterm[3]
        search = Curiterm[4]
        # 当点的后面为非终结符时增大项目集   即  #  A->·B C D...N
        if point< len(Rlist) and (Rlist[point] in self.NotTerminators):
            # 先计算以此非终结符为左侧产生式的向前搜索符集合
            tempset = set()
            flag = True
            for i in range(point+1,len(Rlist)):
                 Curfirst = self.FirstVt[Rlist[i]]
                 if '$' in Curfirst:
                    # 如果first集存在空，则并上first(Yi)-{$},并且继续循环
                    tempset = set(tempset) | (Curfirst - set('$'))
                 else:
                    # 如果first集没有空，则并上当前first集，并且结束循环
                    flag = False
                    tempset = set(tempset) | Curfirst
                    break
            if flag:
                # 如果右边的产生式first集全有空，则还要并上左边的向前搜索符集
                 tempset = set(tempset) | set(search)
            #  对点以后的非终结符作为左侧时的产生式逐个进行遍历
            for pro in self.productionsVT[Rlist[point]]:
                tempitem = (pro[1], Rlist[point], pro[0], 0, tuple(tempset))
                if tempitem not in CLOitem:
                    CLOitem |= self.getCLOSURE(tempitem,CLOitem)
            # 合并项目集中的相同的项目
            # 先将不同的元组的0123(元组形式)作为新字典的key 4作为新字典的value存入字典中去除相同项目再转化为元组存储到到集合中
            tempitemdict = {}
            for i in CLOitem:
                ikey = (i[0], i[1], i[2], i[3])
                if tuple(ikey) not in tempitemdict.keys():
                    tempitemdict[tuple(ikey)] = set()
                tempitemdict[tuple(ikey)] |= set(i[4])
            CLOitem = set()
            for i in tempitemdict.keys():
                Ansitem = (i[0], i[1], i[2], i[3], tuple(tempitemdict[i]))
                CLOitem.add(tuple(Ansitem))
        return CLOitem

    # 建立LR分析表
    def createLRTable(self):
        # 以字典形式创建项目集 key为id value为节点
        # 以字典形式存储项目的clousre闭包  key为项目集集合的各个元组为元素组成的新元组，value为此闭包的id
        Status = {}
        SCLOitem = {}

        def getLRDFANode(id):
            if id in Status:
                return Status[id]
            else:
                NewNode = LRDFANode(id)
            return NewNode
        # 建立初始项目集 I0
        start_id = 0
        start_node = getLRDFANode(start_id)
        # 计算初始项目的closure闭包
        start_CLOitem = self.getCLOSURE((0, 'SSSTART', ('START',), 0, ('#',)), set())
        # 将closure闭包加入初始项目集
        start_node.addItemsets(start_CLOitem)
        SCLOitem[tuple(start_CLOitem)] = start_id
        Status[start_id] = start_node
        # 广度优先算法BFS 开始构建项目集族
        queue = list()
        queue.append(start_node)
        Mid = 0
        while queue:
            now_node = queue.pop(0)
            now_itemsets = now_node.itemsets
            now_id = now_node.id
            is_visit = set()
            # 对项目集中的每个产生式
            for item in now_itemsets:
                if item in is_visit:
                    continue
                is_visit.add(item)
                index = item[0]
                left = item[1]
                Rlist = item[2]
                point = item[3]
                search = item[4]
                # 当点在最后或者产生式的右边有空时进行归约操作
                if point>= len(Rlist) or ('$' in Rlist):
                    if now_id not in self.LRTable.keys():
                        self.LRTable[now_id]={}
                    for s in search:
                        # 归约到不同的产生式
                        if s in self.LRTable[now_id].keys():
                            # 规约-规约冲突
                            print('当前文法不属于LR(1)文法！！')
                            print('发生了规约-规约冲突！')
                            return
                        # 形成LR(1)分析表中的归约式
                        self.LRTable[now_id][s]=('r', index)
                # 若点在中间，则移动点获得新的项目集
                else:
                    # 点向后移一位得到一个新项目集
                    next_iterm = (index, left, Rlist, point+1,search)
                    # 求新项目的closure闭包
                    next_CLOitem = self.getCLOSURE(next_iterm,set())
                    next_cin = Rlist[point]
                    # 遍历上一个项目集中所有可以输入next_cin的产生式 对其进行 闭包 并入
                    for i in now_itemsets:
                        if i in is_visit:
                            continue
                        iright = i[2]
                        ipoint = i[3]
                        # 若点在中间并且点右边的字符正好为 next_cin
                        if ipoint < len(iright) and iright[ipoint] == next_cin:
                            is_visit.add(i)
                            i_CLOitem = (i[0], i[1], i[2], ipoint + 1, i[4])
                            next_CLOitem |= self.getCLOSURE(i_CLOitem, set())
                    # 合并新项目集中的相同的项目
                    # 先将不同的元组的0123(元组形式)作为新字典的key 4作为新字典的value存入字典中去除相同项目再转化为元组存储到到集合中
                    new_item_set = {}
                    for item in next_CLOitem:
                        item_key = (item[0], item[1], item[2], item[3])
                        if tuple(item_key) not in new_item_set.keys():
                            new_item_set[tuple(item_key)] = set()
                        new_item_set[tuple(item_key)] |= set(item[4])
                    next_item_set = set()
                    for key in new_item_set.keys():
                        final_item = (key[0], key[1], key[2], key[3], tuple(new_item_set[key]))
                        next_item_set.add(tuple(final_item))
                    if tuple(next_item_set) in SCLOitem.keys():  # 该项目集已经处理过
                        next_node_id = SCLOitem[tuple(next_item_set)]
                    else:  # 新建一个项目集
                         Mid += 1
                         next_node_id = Mid
                         SCLOitem[tuple(next_item_set)] = next_node_id
                         next_node = getLRDFANode(next_node_id)
                         next_node.addItemsets(next_item_set)
                         Status[next_node_id] = next_node
                         queue.append(next_node)
                    if now_id not in self.LRTable.keys():  # 为当前项目集在LR分析表中创立表项
                         self.LRTable[now_id] = {}
                    # 移进-规约冲突
                    if Rlist[point] in self.LRTable[now_id].keys():
                         print('当前文法不属于LR(1)文法！！！')
                         print('发生了移进-规约冲突！')
                         return
                    if Rlist[point] in self.terminators:
                        self.LRTable[now_id][Rlist[point]] = ('S', next_node_id)
                    else:
                        self.LRTable[now_id][Rlist[point]] = ('G', next_node_id)
        output = open('Action_and_Goto.data', 'w+')
        for id in self.LRTable.keys():
            for i in self.LRTable[id].keys():
                ans = str(self.LRTable[id][i][0]) + str(self.LRTable[id][i][1])
                output.write('[%s,%s]=%s\t' % (str(id), str(i), ans))
            output.write('\n')
        output.close()

    def runOnLRTable(self, tokens):
        # 将tokens列表反向排序
        tokens.reverse()
        # 有一状态栈，有一符号栈
        status_stack = [0]
        symbol_stack = ['#']
        isacc = False
        # 记步数
        count = 0
        while True:
            count += 1
            # 取状态栈最后一个元素
            top_status = status_stack[-1]
            # 取token列表最后一个元素
            token = tokens[-1][1]
            line_index = tokens[-1][0]
            print('步骤: ' + str(count))
            print('符号栈:')
            print(symbol_stack)
            print('输入符号: ' + token)
            print('状态栈:')
            print(status_stack)
            print()
            # 如果token是LR(1)分析表中的输入元素 则根据分析表进行状态转移
            if token in self.LRTable[top_status].keys():
                act = self.LRTable[top_status][token]
                #  状态转移操作
                if act[0] == 'S':
                    # 将要转移的状态移入到状态栈
                    status_stack.append(act[1])
                    # 将移入的token内容符号移入到符号栈
                    symbol_stack.append(token)
                    # 删除列表中最后一个元素（刚刚移入的元素被删除）
                    tokens = tokens[:-1]
                #  进行归约
                elif act[0] == 'r':
                    # 第0行: S'-> S  acc  符合语法
                    if act[1] == 0:
                        isacc = True
                        break
                    # 得到规约产生式
                    production = self.productions[act[1]]
                    # 取规约产生式的左部分
                    left = list(production.keys())[0]
                    # 规约至产生式左侧的非终结符 并将其加入到当前token序列
                    tokens.append((line_index, left))
                    # 如果不需要修改两个栈
                    if production[left] == ['$']:
                        continue
                    # 修改两个栈 去掉规约掉的符号和状态
                    Rlength = len(production[left])
                    status_stack = status_stack[:-Rlength]
                    symbol_stack = symbol_stack[:-Rlength]
                else:
                    # 根据GOTO表在规约后跳转到该有的符号和状态
                   status_stack.append(act[1])
                   symbol_stack.append(token)
                   tokens = tokens[:-1]
            else:
                # 错误，无法状态转移
                print('行号: %s' % line_index)
                print('发现: %s' % token)
                print('期待字符为:')
                for exp in self.LRTable[top_status].keys():
                    print(exp)
                break
        return isacc

    # 语法分析
    def analysis(self, filename):
        token_table = open(filename, 'r')
        tokens = []
        for line in token_table:
            # 读取每一行并且去除掉最后一个'\n'
            line = line[:-1]
            hang = line.split(' ')[1]
            token_type = line.split(' ')[2]
            if token_type == 'identifier' or token_type == 'constant':
                tokens.append((hang, token_type))
            else:
                token = line.split(' ')[3]
                tokens.append((hang, token))
        tokens.append((str(0), '#'))
        isacc = self.runOnLRTable(tokens)
        if isacc:
            print('源代码字符串符合此 2º型文法!')
        else:
            print('源代码字符串不符合此 2º型文法!')


if __name__ == '__main__':
    syn_ana = SynAnalysis()
    syn_ana.ReadSynGrammar('Grammar2.txt')
    syn_ana.initTerminatorsAndNot()
    syn_ana.GetFirstVt()
    syn_ana.createLRTable()
    syn_ana.analysis('token_table.data')
    os.system("pause")
