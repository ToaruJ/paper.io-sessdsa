def play(stat, storage):
    # 判断点是否在地图内，防止撞墙
    def inwall(size, point):
        # point[0]为点的横坐标，point[1]为点的纵坐标
        return 0 <= point[0] < size[0] and 0 <= point[1] < size[1]

    # 从点pa到点pb的最短路径长度
    def ppdistance(pa, pb):
        return abs(pa[0] - pb[0]) + abs(pa[1] - pb[1])

    # 判断point点的东南西北之中可扩张的方向（未占有区域方向）
    def nline(sta, point):
        direct = ((1, 0), (0, 1), (-1, 0), (0, -1))
        nlinelst = []  # 用于储存可扩张的方向
        for dire in range(4):  # 遍历东西南北四个方向
            x, y = point[0] + direct[dire][0], point[1] + direct[dire][1]  # 朝某方向行进所得的新坐标
            if inwall(sta['size'], (x, y)):  # 如果新坐标在地图里
                if sta['now']['fields'][x][y] != sta['now']['me']['id']:  # 并且新坐标不在自己领地内
                    nlinelst.append(dire)  # 则储存此坐标
        return nlinelst

    # 判断顶点的四个顶点之中有几个可以占领并返回有几个未占有顶点
    def ncorner(sta, point):
        cnt = 0  # 用于记录未占领顶点的数量
        direct = ((1, -1), (1, 1), (-1, 1), (-1, -1))  # 东北，东南，西南，西北四个方向
        for dire in range(4):  # 遍历四个方向的四个顶点
            x, y = point[0] + direct[dire][0], point[1] + direct[dire][1]  # 某个方向上的顶点坐标
            if inwall(sta['size'], (x, y)):  # 如果此顶点存在即在地图内
                if sta['now']['fields'][x][y] != sta['now']['me']['id']:  # 并且此顶点不在自己领地内
                    cnt += 1  # 计数器数值加一
        return cnt

    # 算出centerp点到某方纸带band的最短距离
    # centerp是起始点，dire是起始点的朝向，band填storage['meBand']或['enemyBand']
    # otherplayer是某玩家纸卷的坐标（一般是band的所有者）
    def bdistance(centerp, dire, band, otherplayer):
        mindis = ppdistance(centerp, otherplayer)  # 从otherplayer的纸卷开始遍历
        nearp = otherplayer  # 用于记录取最小值时对应的纸带上的点
        if len(band) > 1:  # 用于判断是否需要进行循环
            # 对纸带的每个点算距离，取最小值
            for point in band:
                ppdis = 2 if orient(centerp, dire,
                                    point) == 'BB' else 0  # 如果point点在centerp点的正后方，那么需要先进行一步掉头即在正常两点距离基础上加2
                ppdis += ppdistance(point, centerp)  # ppdis用于记录certerp点纸带上点距离
                if ppdis < mindis:  # 如果certerp点到纸带上点的距离小于原来记录的最小值即mindis
                    mindis = ppdis  # mindis的值替换为此时的ppdis值
                    nearp = point
        return mindis, nearp

    # 算出centerp点到某一方领地的最短距离
    # centerp是起始点,fieldid是某一方玩家的id
    # backUnavail：'No'是可以搜索正后方，'weak'是不能搜正后方，'strong'是不能搜后方某个角度范围
    # dire是centerp点的朝向，manxdeep是最大搜索深度即可以搜索的最大范围
    # 输出最近距离和最近点
    def fdistance(sta, centerp, fieldid, backUnavail, dire=None, maxdeep=None):
        field = sta['now']['fields']
        size = sta['size']
        # 在maxdeep没有初始值时要对maxdeep进行计算，即分别在东西和南北方向上到边界的最大距离
        maxdeep = max(size[0] - centerp[0] - 1, centerp[0]) + max(size[1] - centerp[1] - 1, centerp[1]) \
            if maxdeep is None else maxdeep  # 如果maxdeep有初始值则可跳过此步操作
        # 按照距离从近到远的顺序进行广度优先搜索
        for dis in range(maxdeep + 1):
            for xdis in range(-dis, dis + 1):
                for point in ((centerp[0] + xdis, centerp[1] + dis - abs(xdis)),
                              (centerp[0] + xdis, centerp[1] - dis + abs(xdis))):
                    # 如果point点在玩家领地内，则说明该point点就是领地内到centerp点最短距离的点，此时对应的dis就是point点与centerp点之间的最短距离
                    if inwall(size, point) and field[point[0]][point[1]] == fieldid:
                        if backUnavail == 'No':
                            backeval = True  # backeval用于判断可否对point点进行搜索
                        else:
                            ori = orient(centerp, dire, point)  # point点在centerp点的大致方位
                            backeval = (ori != 'BB') if backUnavail == 'weak' else not (
                                        'BB' in ori)  # 在‘weak’的情况下，只要point点不在centerp点的正后方就可以搜索；在‘strong’的情况下，只要point点不在正后方附近的很小范围内就可以搜索
                        if backeval:  # 如果可以对point点进行搜索，则进行输出
                            return dis, point
        return maxdeep + 1, (None, None)  # 防止出现bug

    # 判断点point在参考点centerp的相对方向
    # dire是centerp点的指向
    def orient(centerp, dire, point):
        # 计算相对方位的，reladic[0]是point在centerp前方的距离，reladic[1]是point在centerp右方的距离
        # reladic中的数据分别为point在东边的距离，point在南边的距离，point在西边的距离，point在北边的距离，当用dire切片之后，就变成point在centerp前边以及右边的距离
        reladic = (point[0] - centerp[0], point[1] - centerp[1], centerp[0] - point[0],
                   centerp[1] - point[1], point[0] - centerp[0])[dire:dire + 2]
        if reladic == (0, 0):  # point与centerp处于同一位置
            return 'FFBB'
        elif abs(reladic[1]) * 3 < abs(reladic[0]):  # point大致位于centerp的正前/后方
            if reladic[0] > 0:
                return 'FF' if reladic[1] == 0 else 'RFF' if reladic[1] > 0 else 'LFF'  # 分别为：正前方，前方稍偏右，前方稍偏左
            else:
                return 'BB' if reladic[1] == 0 else 'RBB' if reladic[1] > 0 else 'LBB'  # 分别为：正后方，后方稍偏右，后方稍偏左
        elif abs(reladic[0]) * 3 < abs(reladic[1]):  # point大致位于centerp的正左/右方
            if reladic[1] > 0:
                return 'RR' if reladic[0] == 0 else 'RRF' if reladic[0] > 0 else 'RRB'  # 分别为：正右方，右方稍偏前，右方稍偏后
            else:
                return 'LL' if reladic[0] == 0 else 'LLF' if reladic[0] > 0 else 'LLB'  # 分别为：正左方，左方稍偏前，左方稍偏后
        else:  # 其余情况则依次归为右前，左前，右后，左后
            if reladic[0] > 0:
                return 'RF' if reladic[1] > 0 else 'LF'
            else:
                return 'RB' if reladic[1] > 0 else 'LB'

    # 用于估计前进（直行）扩张需要的步数
    # start用于判断是否已经开始扩张
    # assess模式是还在领地内shift时预算能走的步数
    # assess只用于routeAssess，其中包含三元参数，assess[0]是目前的位置，assess[1]是扩张终点，assess[2]是当前到达目标点所需要的转弯数
    def restep(sta, stor, dire, start=False, assess=None):
        # 变量名简化
        if assess is None:  # 如果assess没有初始参数值，则需要进行初始化
            myp = (sta['now']['me']['x'], sta['now']['me']['y'])
            endpx, endpy = stor['strategy']['endp'][0], stor['strategy']['endp'][1]
            turn = stor['strategy']['turn']  # 预计转弯数
        else:  # 如果assess已经有初始参数值，则直接使用
            myp = assess[0]
            endpx, endpy = assess[1][0], assess[1][1]
            turn = assess[2]
        enmp = (sta['now']['enemy']['x'], sta['now']['enemy']['y'])
        mxdeep = ppdistance(myp, enmp) if start else \
            bdistance(enmp, sta['now']['enemy']['direction'], stor['meBand'], myp)[0]  # 计算敌人到自己纸带的最短距离，用于计算自己可扩张的距离
        if turn == 0:  # 如果沿当前方向可以直达结束点
            step = min((endpx - myp[0], endpy - myp[1], myp[0] - endpx, myp[1] - endpy)[dire],
                       mxdeep * 2 // 3)  # 改成*2//3是因为有了更强的防御机制，可以更大胆地扩张；若直达可能被敌人攻击，则需要在保证安全的前提下改变路线
        else:  # 如果仍然需要拐弯才能到达终点
            walldis = (sta['size'][0] - myp[0] - 1, sta['size'][1] - myp[1] - 1, myp[0], myp[1])
            step = min(mxdeep * 2 // ((turn + 1) * 3), walldis[dire])  # 在保证安全的前提下尽可能向地图边界扩张
        return step

    # 估算可扩充的领地大小
    # p1，p2为任意点
    def fillnum(sta, p1, p2):
        # 以p1点和p2点为对角线顶点可以确定一个矩形
        nw = (min(p1[0], p2[0]), min(p1[1], p2[1]))  # 矩形的左上顶点
        se = (max(p1[0], p2[0]), max(p1[1], p2[1]))  # 矩形的右下顶点
        cnt = 0  # 用于记录样本点的数量
        stepargv = []  # 用于记录样本点间隔，第一项是东西向边上的样本点间隔，第二项是南北向边上的样本点间隔
        # 根据p1，p2围城面积的大小取样本点间隔，是跳着选取样本点估计可扩充面积
        for i in range(2):
            # 不同长度范围对应不同样本点间隔，最大为5
            for argv in ((10, 1), (20, 2), (30, 3), (40, 4)):
                if argv[0] - (se[i] - nw[i]) < 10:
                    stepargv.append(argv[1])
                    break
            else:
                stepargv.append(5)
        # 选取样本点估算未成为自己领地的点数
        for x in range(nw[0], se[0] + 1, stepargv[0]):
            for y in range(nw[1], se[1] + 1, stepargv[1]):
                if sta['now']['fields'][x][y] != sta['now']['me']['id']:
                    cnt += 1  # 记录不在自己领地内的样本点数
            return cnt * stepargv[0] * stepargv[1]  # 返回估算得到的未占领点数即该矩形内可扩充的领地大小

    # 估计运行shift模式时当前的最佳前进方向
    def shiftto(sta, stor, start=False):
        direct = ((1, 0), (0, 1), (-1, 0), (0, -1))
        x, y, mydire = sta['now']['me']['x'], sta['now']['me']['y'], sta['now']['me']['direction']
        # direlst是优先的转向方向，sublst是次一级的，当direlst为空时采用
        direlst, sublst = [], []
        turndic = {mydire: 'F', (mydire - 1) % 4: 'L', (mydire + 1) % 4: 'R'}
        # 在shift模式走到下一个扩张出发点，无cd冷却
        if 'assessCD' not in stor['strategy']:
            ori = orient((x, y), mydire, stor['strategy']['nextstart'])  # 下一个扩张出发点的相对方向
            for dire in (mydire, (mydire - 1) % 4, (mydire + 1) % 4):  # 分别查找前、左、右三个方向
                point = (x + direct[dire][0], y + direct[dire][1])  # 在该方向上前进一步所得到的坐标
                if inwall(sta['size'], point) and turndic[dire] in ori:  # 如果下一个扩张出发点在目前查找的方向上
                    sublst.append(dire)  # 则先将此方向作为次级转向方向
                    if sta['now']['fields'][point[0]][point[1]] == sta['now']['me']['id']:
                        direlst.append(dire)
            if direlst:
                turn = turndic[direlst[0]]  # 优先记录一级转向方向
            elif start:  # 已经找到下一个扩张出发点
                if stor['lastturn'][0] == 'R':
                    # 如果再上一个拐角处右拐的话则尽量右拐，便于形成闭合曲线，更快地back，同时保证自身安全
                    turn = 'R' if inwall(sta['size'], (x + direct[(mydire + 1) % 4][0],
                                                       y + direct[(mydire + 1) % 4][1])) else 'L'
                else:
                    # 在上一个拐角处左拐的话同理
                    turn = 'L' if inwall(sta['size'], (x + direct[(mydire - 1) % 4][0],
                                                       y + direct[(mydire - 1) % 4][1])) else 'R'
            else:
                turn = turndic[sublst[0]]  # 最后才记录次级转向方向
        # shift处于CD冷却中，漫游
        else:
            for dire in (mydire, (mydire - 1) % 4, (mydire + 1) % 4):
                point = (x + direct[dire][0], y + direct[dire][1])
                if inwall(sta['size'], point):
                    sublst.append(dire)
                    if sta['now']['fields'][point[0]][point[1]] == sta['now']['me']['id']:
                        direlst.append(dire)
            turn = turndic[direlst[0]] if direlst else turndic[sublst[0]]
        return turn

    # 在back模式走回自己领地
    def backto(sta, stor, start=False):
        direct = ((1, 0), (0, 1), (-1, 0), (0, -1))
        myx, myy = sta['now']['me']['x'], sta['now']['me']['y']
        mydire = sta['now']['me']['direction']
        enmx, enmy = sta['now']['enemy']['x'], sta['now']['enemy']['y']
        # direlst是优先的转向方向，sublst是次一级的，当direlst为空时采用
        direlst, sublst = [], []
        turndic = {mydire: 'F', (mydire - 1) % 4: 'L', (mydire + 1) % 4: 'R'}  # 各方向相对于自身的方位
        antiturn = {'L': (mydire + 1) % 4, 'R': (mydire - 1) % 4, 'F': (mydire - 2) % 4}  # 自身方位对应的方向
        endp = stor['strategy']['endp']
        # 确定搜索方向的优先级，先直行还是先转弯
        # 两个Rela分别记录终止点、敌方在前方、右方的距离
        meEndpRela = (endp[0] - myx, endp[1] - myy, myx - endp[0],
                      myy - endp[1], endp[0] - myx)[mydire:mydire + 2]
        meEnmRela = (enmx - myx, enmy - myy, myx - enmx,
                     myy - enmy, enmx - myx)[mydire:mydire + 2]
        if meEndpRela[0] * meEnmRela[0] <= 0:
            searchOrder = (mydire, (mydire - 1) % 4, (mydire + 1) % 4)  # 如果终止点与敌人一前一后，那么优先搜索前方
        elif meEndpRela[1] * meEnmRela[1] < 0 or (abs(meEndpRela[0]) < abs(meEnmRela[0])
                                                  and abs(meEndpRela[1]) > abs(
                    meEnmRela[1])):  # 如果终止点与敌人前后方向上处于同一侧，但是一左一右或者前后方向上到终止点较近，并且终止点在左右方向较远
            searchOrder = ((mydire - 1) % 4, mydire, (mydire + 1) % 4) if meEndpRela[1] < 0 \
                else ((mydire + 1) % 4, mydire, (mydire - 1) % 4)  # 如果终止点在左边就优先搜左边，否则优先搜右边
        else:
            searchOrder = (mydire, (mydire - 1) % 4, (mydire + 1) % 4)
        # 开始按方向搜索可行性
        for dire in searchOrder:
            point = (myx + direct[dire][0], myy + direct[dire][1])  # 沿某一方向前进所得的点
            if inwall(sta['size'], point) and sta['now']['bands'] \
                    [point[0]][point[1]] != sta['now']['me']['id']:  # 如果该点在地图内并且没有撞自己纸带
                sublst.append(dire)  # 那么就可以在次级搜索方向中添加这个方向
                if stor['strategy']['path'][dire] > 0:
                    direlst.append(dire)
        if direlst:  # 只要direlst存在就按照这个方向拐弯
            turn = turndic[direlst[0]]
        elif start:
            if stor['lastturn'][0] == 'R':
                # 如果上一个拐弯处为右拐，那么优先左拐，因为这样可以避免转圈，可以更快地回到领地
                turn = 'L' if inwall(sta['size'], (myx + direct[(mydire - 1) % 4][0],
                                                   myy + direct[(mydire - 1) % 4][1])) else 'R'
            else:
                # 在上一个拐弯处左拐的情况同理
                turn = 'R' if inwall(sta['size'], (myx + direct[(mydire + 1) % 4][0],
                                                   myy + direct[(mydire + 1) % 4][1])) else 'L'
            stor['strategy']['path'][antiturn[turn]] += 1  # 记录回家的路径
        else:
            turn = turndic[sublst[0]]
            stor['strategy']['path'][antiturn[turn]] += 1
        return turn

    # attack模式前往某目标点
    def attackto(sta, stor):
        myx, myy = sta['now']['me']['x'], sta['now']['me']['y']
        enemyx, enemyy = sta['now']['enemy']['x'], sta['now']['enemy']['y']
        mydire, enmdire = sta['now']['me']['direction'], sta['now']['enemy']['direction']
        aimp = stor['strategy']['endp']  # 计划攻击的点
        direct = ((1, 0), (0, 1), (-1, 0), (0, -1))
        ori = orient((myx, myy), mydire, aimp)  # 攻击点在当前位置的大致方位
        direlst, sublst = [], []  # 一级搜索方向&次级搜索方向
        turndic = {mydire: 'F', (mydire - 1) % 4: 'L', (mydire + 1) % 4: 'R'}  # 各方向相对当前位置的方位
        # 设定搜索方向的顺序：在前后方向时都是先搜前方，在右边时先搜索右边，在左边时先搜索左边（其余两个方向采取逐渐远离第一方向的顺序）
        searchOrder = (mydire, (mydire - 1) % 4, (mydire + 1) % 4) if (enmdire - mydire) % 4 == 1 else \
            (mydire, (mydire + 1) % 4, (mydire - 1) % 4) if (enmdire - mydire) % 4 == 3 else \
                ((mydire + 1) % 4, mydire, (mydire - 1) % 4) if 'R' in ori else \
                    ((mydire - 1) % 4, mydire, (mydire + 1) % 4)
        # 对左前右三个方向搜索可行性
        for dire in searchOrder:
            point = (myx + direct[dire][0], myy + direct[dire][1])  # 沿某一方向搜索得到的点
            if inwall(sta['size'], point) and sta['now']['bands'] \
                    [point[0]][point[1]] != sta['now']['me']['id']:  # 如果该点在地图内且不在我方纸带上
                sublst.append(dire)  # 则先保存到次级搜索方向
                if turndic[dire] in ori:  # 如果该方向与攻击点的大致方位一致
                    direlst.append(dire)  # 则直接当作一级搜索方向
        # 可能出现头对头攻击
        if aimp == (enemyx, enemyy):
            # reladic是攻击点在前面 ，右边的距离
            reladic = (aimp[0] - myx, aimp[1] - myy, myx - aimp[0],
                       myy - aimp[1], aimp[0] - myx)[mydire:mydire + 2]
            ppdis = ppdistance((myx, myy), aimp)  # 我方到攻击点的距离
            # 两者距离为奇数，可以骚操作玩侧碰
            if stor['attackActive']:
                limit = 1 if ppdis == 3 else 0
                notOver = reladic[0] not in (1, -1, -2, -3) if ppdis == 3 else reladic[
                                                                                   0] > 0  # 前者为被碰或者将碰上，后者判断是否已经结束比赛即是否已经碰上
                straightF = reladic[1] != 0 if ppdis == 3 else True
            # 两者距离为偶数，尽可能防止被侧碰
            else:
                limit = 0
                notOver = reladic[0] > 0  # 碰上则比赛结束
                straightF = True
            # 对于不同的方向，有判断其可行的不同标准，存在direEsti中
            direEsti = {mydire: notOver and straightF, (mydire - 1) % 4: reladic[1] < -limit,
                        (mydire + 1) % 4: reladic[1] > limit}
            for dire in direlst:
                if direEsti[dire]:  # 如果存储在direlst中的方向可行
                    turn = turndic[dire]  # 直接应用
                    break
            else:
                turn = turndic[sublst[0]] if sublst[0] != mydire else turndic[sublst[1]] \
                    if len(sublst) > 1 else 'N'  # 取sublst中不与mydire相同的方向，如果没有则记为N
        else:
            turn = turndic[direlst[0]] if direlst else turndic[sublst[0]]  # 依照优先级选取拐弯方向
        return turn

    # 刷新边界点（meback给True、False，分别表示自己扩回到领地以及敌人回到领地）
    def reBounder(sta, stor, meback):
        # 自己回到领地，重算边界点
        if meback:
            for point in tuple(stor['bounder']):  # 遍历原来边界上的所有点
                ncor = ncorner(sta, point)  # 原来边界点正方形中可以扩张的顶点数
                # point点变为自己领地内或莫名消失
                if ncor == 0 or sta['now']['fields'][point[0]][point[1]] != sta['now']['me']['id']:
                    stor['bounder'].remove(point)  # 直接在边界中删除该点
            for point in tuple(stor['bounder']):
                ncor = ncorner(sta, point)
                if ncor == 2 or (ncor == 1 and nline(sta,
                                                     point)):  # 有两个可扩张顶点或者有一个可扩张顶点以及至少一个可扩张方向，说明仍在边界上（但必然不是边界顶点，因为边界顶点正方形中一定有三个可扩张顶点）
                    for p2 in [(point[0], point[1] + i) for i in range(-4, 5) if i != 0] + \
                              [(point[0] + i, point[1]) for i in range(-4, 5) if i != 0]:  # 搜索point附近的点
                        # 该point离其他记录点过近，且不是顶点，没必要保留，直接删去
                        if inwall(sta['size'], p2) and p2 in stor['bounder']:
                            stor['bounder'].remove(point)
                            break
            # 把刚刚expand模式的记录点即新生成的边界存起来
            for point in stor['unsaveBounder']:
                stor['bounder'].add(point)
            stor['unsaveBounder'].clear()  # 清空unsaveBounder
        # 敌人回到领地，重算边界点（如果敌人侵占了我方领地那么只有在敌人回到领地之后才生效）
        else:
            eaten = False
            for point in tuple(stor['bounder']):  # 遍历原来的边界点
                if sta['now']['fields'][point[0]][point[1]] != sta['now']['me']['id']:  # 如果发现有的边界点不在自己的领地之内了
                    eaten = True  # 就说明这个点被地方侵占了
                    stor['bounder'].remove(point)  # 直接在原来的边界点中删掉这个点
            # 发现有点被敌方吃掉
            if eaten and stor['enemyBand']:
                step = 0
                search = {'x': ((-1, 0), (1, 0)), 'y': ((0, -1), (0, 1)),
                          't': ((-1, -1), (-1, 1), (1, 1), (1, -1)),
                          'start': ((i, j) for i in range(-1, 2) for j in range(-1, 2))}
                # 沿着敌方纸带两侧寻找
                for i in range(len(stor['enemyBand']) - 1):
                    bandp = stor['enemyBand'][i]  # 遍历敌方纸带上的点
                    if i == 0:
                        searchdire = 'start'  # 对于纸带的起始点，根据‘start’进行范围搜索
                    elif stor['enemyBand'][i - 1][0] == stor['enemyBand'][i][0] == stor['enemyBand'][i + 1][0]:
                        searchdire = 'x'  # 如果纸带上连续三个点横坐标相同，说明纸带纵向延伸，进行水平方向搜索
                    elif stor['enemyBand'][i - 1][1] == stor['enemyBand'][i][1] == stor['enemyBand'][i + 1][1]:
                        searchdire = 'y'  # 如果纸带上连续三个点纵坐标相同，说明纸带横向延伸，进行竖直方向搜索
                    else:
                        searchdire = 't'  # 对于没有规律的点则搜索四个顶点
                    for arg in search[searchdire]:
                        point = (bandp[0] + arg[0], bandp[1] + arg[1])  # 从纸带上某点沿搜索方向得到的点
                        # 发现敌方纸带两侧有自己领地即延伸出来的点位于我方领地内
                        if inwall(sta['size'], point) and sta['now']['fields'] \
                                [point[0]][point[1]] == sta['now']['me']['id']:
                            ncor = ncorner(sta, point)  # 用于判断这个点是不是我方区域的顶点
                            # 敌方纸带两侧有自己领地的顶点
                            if ncor == 3 or (ncor == 1 and not nline(sta, point)):
                                stor['bounder'].add(point)
                                step = 1  # 从顶点开始计数
                            # 敌方纸带两侧有自己领地的边界，隔8个点存一次自己的边界点
                            elif step % 8 == 0 and searchdire != 't':
                                stor['bounder'].add(point)
                    step += 1  # 每搜索一个点增加一步

    # 评估出发点能扩大多大领地
    # nowp自己位置，availp储存可以的出发策略，dire出发方向，startp是从领地扩张的出发位置，
    # endp领地扩张结束位置，ori相对方向，step是扩张步数（单次不转弯）
    def pointAssess(sta, availp, nowp, dire, startp, endp, ori, step):
        direct = ((1, 0), (0, 1), (-1, 0), (0, -1))
        enemydis = ppdistance(startp, (sta['now']['enemy']['x'], sta['now']['enemy']['y']))  # 敌人到自己现在位置的距离
        fillcnt = None
        # 出发前的估计
        if abs(endp[0] - nowp[0]) < 4 and abs(endp[1] - nowp[1]) < 4:  # 当前点距离endp足够近，可以认为这两个点都在正方形的一个顶点附近，可以延展出四条边
            # 当前位置在endp的相对方向
            enddire = (dire - 1) % 4 if 'L' in ori else (dire + 1) % 4
            p1 = (startp[0] + step * direct[dire][0], startp[1] + step * direct[dire][1])  # step是一次直线走的总步数，p1是第一个拐点
            p2x = endp[0] + step * direct[enddire][0]  # p2是最后一个拐点
            p2x = p2x if 0 <= p2x < sta['size'][0] else 0 if p2x < 0 else sta['size'][
                                                                              0] - 1  # 首先判断得到的横坐标是不是在地图内，如果不在则就近取到边界
            p2y = endp[1] + step * direct[enddire][1]
            p2y = p2y if 0 <= p2y < sta['size'][1] else 0 if p2y < 0 else sta['size'][1] - 1
            length = step * 4 + 1  # 一次扩张的最大距离
            if length < enemydis:  # 确定可以扩张
                fillcnt = fillnum(sta, p1, (p2x, p2y))
        elif 'FF' in ori:  # 如果endp在出发点的前方
            length = ppdistance(startp, endp) + 1
            if length < enemydis:  # 确定可以扩张
                if dire % 2 == 0:  # 出发方向平行于x轴的情况
                    fillcnt = min(fillnum(sta, startp, (endp[0], min(endp[1] + max(15, step),
                                                                     sta['size'][1] - 1))),
                                  fillnum(sta, startp, (endp[0],
                                                        max(endp[1] - max(15, step), 0))))
                else:
                    fillcnt = min(fillnum(sta, startp, (min(endp[0] + max(15, step),
                                                            sta['size'][0] - 1), endp[1])), fillnum(sta, startp,
                                                                                                    (max(endp[0] - max(
                                                                                                        15, step), 0),
                                                                                                     endp[1])))
        elif ori in ('LF', 'RF'):  # 在大致右前方或大致左前方时，可以确保走一段路程可以圈得相当大的面积
            length = ppdistance(startp, endp) + 1  # 起点和终点分别在正方形的对角
            if length < enemydis:  # 确定可以扩张
                fillcnt = fillnum(sta, startp, endp)
        else:  # 其他情况，可以视作起点和终点在正方形的一条边上，因此需要先从起点走到终点的对角
            length = ppdistance((startp[0] + step * direct[dire][0], startp[1]
                                 + step * direct[dire][1]), endp) + step + 1  # 总长度为从起点走到终点的对角再走到终点的距离
            if length < enemydis:  # 确定可以扩张
                fillcnt = fillnum(sta, (startp[0] + step * direct[dire][0], startp[1] + step * direct[dire][1]), endp)
        if fillcnt:  # 如果已经算好，那么存储数据
            availp.append({'startp': startp, 'direction': dire, 'endp': endp,
                           'efficient': fillcnt / (length + ppdistance(nowp, startp))})

    # pointAssess的循环
    def routeAssess(sta, stor):
        x, y = sta['now']['me']['x'], sta['now']['me']['y']
        availp = []
        # 取最近的15个点计算最佳扩张路径
        if len(stor['bounder']) > 15:  # 如果边界上有大于15个点
            pointlst = sorted(stor['bounder'], key=lambda p: ppdistance((x, y), p))[:15]  # 则选择最近的15个点
        else:  # 如果边界上的点不足15个
            pointlst = tuple(stor['bounder'])  # 则取全部点
        for point in pointlst:  # 遍历所有选定的点
            for dire in nline(sta, point):  # 每个点遍历所有可行方向
                for endp in stor['bounder']:  # 遍历边界所有的点作为终止点
                    ori = orient(point, dire, endp)  # 终止点在当前点的相对方向
                    if 'BB' not in ori:  # 只要终止点不是在当前点的后面
                        if abs(endp[0] - x) < 4 and abs(endp[1] - y) < 4:
                            turn = 2
                        else:
                            turn = 0 if 'FF' in ori else 1 \
                                if 'F' in ori else 2
                        step = restep(sta, stor, dire, True, (point, endp, turn))
                        pointAssess(sta, availp, (x, y), dire, point, endp, ori, step)
        if len(availp) > 1:
            return max(*availp, key=lambda p: p['efficient'])  # 如果availp中存储了多个方案，返回效率最高的方案
        return availp[0] if availp else None  # 否则返回唯一的方案或者返回None（无方案可返回时）

    # 扩张模式
    def expand(sta, stor, dire=None, endp=None):
        direct = ((1, 0), (0, 1), (-1, 0), (0, -1))
        x, y = sta['now']['me']['x'], sta['now']['me']['y']  # 我当前的位置
        mydire = sta['now']['me']['direction']  # 我当前的朝向
        # 从别的模式转到扩张模式
        if stor['strategy']['name'] != 'expand':
            stor['strategy'] = {'name': 'expand', 'endp': endp}  # 重新布置strategy
            # 当距离敌方太近时，不宜扩张
            if ppdistance((x, y), (sta['now']['enemy']['x'], sta['now']['enemy']['y'])) < 6:
                stor['strategy'] = {'name': 'expand', 'assessCD': 1}  # 加一次CD，重新选取扩张出发点
                return shift(sta, stor)  # 领地内转移
            else:
                if abs(endp[0] - x) < 4 and abs(endp[1] - y) < 4:  # 如果快要到达终止点
                    stor['strategy']['turn'] = 2  # 在保证安全的前提下可以尽量大地扩张
                else:
                    ori = orient((x, y), dire, endp)  # 记录扩张终止点大致方向
                    stor['strategy']['turn'] = 0 if 'FF' in ori else 1 \
                        if 'F' in ori else 2
                stor['strategy']['step'] = restep(sta, stor, dire, start=True)  # 估计扩张所需要的步数
                stor['strategy']['savep'] = {i for i in range(8, stor['strategy']['step'] - 6, 8)}  # 边上的点每8个存一次
                if (dire - mydire) % 4 != 2:  # 排除dire在mydire正后方的情况，返回dire在mydire的大致方位
                    return {0: 'N', 1: 'R', 3: 'L'}[(dire - mydire) % 4]  # 在正前方的话不用拐弯，因此记为N即None
                # 处理可能dire在mydire正后方的bug，不常见
                else:
                    stor['strategy']['step'] -= 2
                    if inwall(sta['size'], (x + direct[mydire][0], y + direct[mydire][1])):
                        stor['strategy']['expandCD'] = ['R', 'R', 'R', 'L'] if inwall(
                            sta['size'], (x + direct[(mydire - 1) % 4][0],
                                          y + direct[(mydire - 1) % 4][1])) else ['L', 'L', 'L', 'R']
                    else:
                        stor['strategy']['expandCD'] = ['R', 'L', 'L', 'L'] if inwall(
                            sta['size'], (x + direct[(mydire - 1) % 4][0],
                                          y + direct[(mydire - 1) % 4][1])) else ['L', 'R', 'R', 'R']
                    return stor['strategy']['expandCD'].pop()
        # 之前出现expand的罕见状态，需要CD转向
        elif 'expandCD' in stor['strategy']:
            turn = stor['strategy']['expandCD'].pop()
            if not stor['strategy']['expandCD']:
                del stor['strategy']['expandCD']
            return turn
        else:  # 处于扩张模式，继续扩张
            endp = stor['strategy']['endp']
            stor['strategy']['step'] -= 1  # 剩余直行步数
            if stor['strategy']['step'] <= 0:  # 直行到指定点
                stor['unsaveBounder'].append((x, y))  # 记录拐角
                # turn用完，改back模式
                if stor['strategy']['turn'] == 0:
                    turn = back(sta, stor)
                # expand一次转弯
                else:
                    stor['strategy']['turn'] -= 1  # 剩余拐角数减一
                    turn = orient((x, y), mydire, endp)  # endp在当前点的大致方位
                    # 确定该转向的方向
                    if turn[0] not in 'LR':
                        # 如果在上一个拐角是右拐，则在不越出地图的前提下尽量右拐，这样可以更快地back，保证安全
                        if stor['lastturn'][0] == 'R':
                            turn = 'R' if inwall(sta['size'], (x + direct[(mydire + 1) % 4][0],
                                                               y + direct[(mydire + 1) % 4][1])) else 'L'
                        # 在上一个拐角处左拐的话同理
                        else:
                            turn = 'L' if inwall(sta['size'], (x + direct[(mydire - 1) % 4][0],
                                                               y + direct[(mydire - 1) % 4][1])) else 'R'
                    dire = (mydire - 1) % 4 if turn[0] == 'L' else (mydire + 1) % 4  # 拐弯方向对应的具体方向
                    stor['strategy']['step'] = restep(sta, stor, dire)  # 拐弯之后重新估计扩张所需要的步数
                    stor['strategy']['savep'] = {i for i in range(8, stor['strategy']['step'] - 6, 8)}  # 再次每8个点记录一次
                return turn
            # 继续直行
            else:
                if stor['strategy']['step'] in stor['strategy']['savep']:
                    stor['unsaveBounder'].append((x, y))
                return 'N'  # 直行不拐弯

    # 回家模式
    def back(sta, stor, endp=None):
        x, y = sta['now']['me']['x'], sta['now']['me']['y']  # 我方位置
        mydire, enmdire = sta['now']['me']['direction'], sta['now']['enemy']['direction']  # 我方及敌方指向
        enmx, enmy = sta['now']['enemy']['x'], sta['now']['enemy']['y']  # 敌方位置
        finish = False
        # 从别的模式转到back模式
        if stor['strategy']['name'] != 'back':
            stor['strategy'] = {'name': 'back', 'path': [0] * 4}
            if not endp:  # 如果没有终止点，则需要寻找终止点（领地中距离自己最近的点）
                endp = fdistance(sta, (x, y), sta['now']['me']['id'], 'weak', mydire)[1]
            stor['strategy']['endp'] = endp
            xstep, ystep = endp[0] - x, endp[1] - y  # 终止点与自己的横纵坐标之差
            stor['strategy']['step'] = 0
            stor['strategy']['path'] = [xstep if xstep >= 0 else 0, ystep if ystep >= 0 else 0,
                                        -xstep if xstep < 0 else 0, -ystep if ystep < 0 else 0]  # 分别记录在东西和南北方向上走的距离
            turn = backto(sta, stor, True)
            finish = True
        # 如果离敌方纸带很近，考虑走投无路极限反杀
        elif stor['enemyBand'] and ppdistance((x, y), (enmx, enmy)) < 12:
            meToField = ppdistance((x, y), stor['strategy']['endp'])  # 当前位置到终止点的距离
            enmToMe = bdistance((enmx, enmy), enmdire, stor['meBand'], (myx, myy))[0]  # 敌方击杀我方的最短距离
            meToEnm, enmWeakp = bdistance((myx, myy), mydire, stor['enemyBand'], (enmx, enmy))  # 我方击杀敌方的最短距离
            enmToField = fdistance(sta, (enmx, enmy), sta['now']['enemy']['id'], 'No')[0]  # 敌人回领地的最短距离
            if meToField < enmToMe and meToEnm < enmToField:  # 如果我方可以在被击杀前回领地或者可以在敌方回领地之前将其击杀
                turn = attack(sta, stor, enmWeakp)  # 进入攻击模式
                finish = True
        # 原来的返回目的地被占领，大喊一声'fxxk'，然后重算新目的地
        if not finish:
            if sta['now']['fields'][stor['strategy']['endp'][0]] \
                    [stor['strategy']['endp'][1]] != sta['now']['me']['id']:
                stor['strategy'] = {'name': 'fxxk'}
                turn = back(sta, stor)
            # 继续back模式
            else:
                stor['strategy']['path'][mydire] -= 1  # 回到领地的路径数减少
                stor['strategy']['step'] += 1  # 步数不断增加
                if stor['strategy']['step'] % 8 == 0:  # 每8步记录一次边界
                    stor['unsaveBounder'].append((x, y))
                turn = backto(sta, stor)
        return turn

    # 领地内转移shift
    def shift(sta, stor):
        x, y = sta['now']['me']['x'], sta['now']['me']['y']
        start = False
        # 刚回到领地，找下一个出发点，预估下次的最佳扩张路线
        if stor['strategy']['name'] != 'shift':
            nextone = routeAssess(sta, stor)  # 选取可以使扩张范围较大的扩张路线（包含扩张起点，扩张终点，扩张方向等）
            if nextone:  # 如果已经找到下一个扩张点
                stor['strategy'] = {'name': 'shift', 'nextstart': nextone['startp'],
                                    'nextend': nextone['endp'], 'expanddire': nextone['direction']}  # 将这些数据存入strategy中
                start = True
            else:
                stor['strategy'] = {'name': 'shift', 'assessCD': 5}  # 针对routeAssess没有输出的，给一个5轮的CD冷却时间
        if 'assessCD' in stor['strategy']:
            # 5轮的CD结束，之前找不到合适出发点时积聚的怒气爆发出来，
            # 大喊一声'fxxk'，然后重新计算下一个扩张出发点
            if stor['strategy']['assessCD'] == 0:  # CD时间结束
                stor['strategy'] = {'name': 'fxxk'}
                return shift(sta, stor)  # 开始找出发点
            else:
                stor['strategy']['assessCD'] -= 1  # CD时间缩短
                return shiftto(sta, stor)  # 在进行CD冷却时进行漫游
        elif stor['strategy']['nextstart'] == (x, y):  # 如果已经到达扩张出发点
            nextp = stor['strategy']['nextend']  # 扩张终止点
            dire = stor['strategy']['expanddire']  # 扩张方向
            turn = expand(sta, stor, dire, nextp)  # 扩张时的拐点
            return turn
        # 可能计划点已被占领
        else:
            startp = stor['strategy']['nextstart']
            # 计划点被占领，怒吼一声'fxxk'然后重新找点
            if sta['now']['fields'][startp[0]][startp[1]] != sta['now']['me']['id']:
                stor['strategy'] = {'name': 'fxxk'}
                return shift(sta, stor)
            # 继续在领地内shift
            return shiftto(sta, stor, start)

    # 攻击敌人模式
    def attack(sta, stor, endp=None):
        myx, myy = sta['now']['me']['x'], sta['now']['me']['y']
        enmx, enmy = sta['now']['enemy']['x'], sta['now']['enemy']['y']
        mydire, enmdire = sta['now']['me']['direction'], sta['now']['enemy']['direction']
        # 从别的模式转到attack模式
        if stor['strategy']['name'] != 'attack':
            if not endp:  # 没有攻击点时需要先找
                endp = bdistance((myx, myy), mydire, stor['enemyBand'], (enmx, enmy))
            stor['strategy'] = {'name': 'attack', 'endp': endp}
            turn = attackto(sta, stor)  # 进入攻击
        # 敌人成功逃脱（出现这个的概率不高，但还是准备）
        elif sta['now']['fields'][enmx][enmy] == sta['now']['enemy']['id']:
            turn = back(sta, stor)  # 如果敌人逃脱则直接返回我方领地
        # 继续攻击
        else:
            endp = min(stor['strategy']['endp'], stor['enemyBand'][-1],
                       key=lambda p: ppdistance((myx, myy), p))  # 从原来的攻击点、敌方纸带末端、敌方纸卷选取最近点进行攻击
            stor['strategy']['endp'] = endp
            turn = attackto(sta, stor)
        return turn

    # 开始模式，只在一开始时执行
    def startmode(sta, stor):
        x, y = sta['now']['me']['x'], sta['now']['me']['y']
        mydire = sta['now']['me']['direction']
        stor['attackActive'] = ppdistance((x, y), (sta['now']['enemy']['x'],
                                                   sta['now']['enemy'][
                                                       'y'])) % 2 == 1  # 判断我方纸卷到敌方纸卷的距离是否为奇数，用于attack函数中侧碰的情况
        for item in ((x - 1, y - 1), (x - 1, y + 1), (x + 1, y + 1), (x + 1, y - 1)):
            stor['bounder'].add(item)  # 确定初始边界点
        ori = orient((x, y), mydire, (sta['now']['enemy']['x'], sta['now']['enemy']['y']))  # 记录此时敌方的大致方位
        if 'L' in ori:
            nextp = [point for point in stor['bounder'] \
                     if orient((x, y), mydire, point) == 'RF'][0]  # 当敌方在左边时，往右前方扩张
        else:
            nextp = [point for point in stor['bounder'] \
                     if orient((x, y), mydire, point) == 'LF'][0]  # 当敌方在右边时，往左前方扩张
        stor['strategy'] = {'name': 'shift', 'nextstart': nextp}
        turn = shiftto(sta, stor)  # 寻找扩张起始点
        antidire = {'L': -1, 'N': 0, 'F': 0, 'R': 1}  # 方向改变量
        stor['strategy']['expanddire'] = (mydire + antidire[turn]) % 4  # 扩张方向=初始方向+方向改变量
        stor['strategy']['nextend'] = [p for p in stor['bounder']
                                       if orient(nextp, stor['strategy']['expanddire'], p)[1] != 'B'][
            0]  # 取位于nextp前方一定角度范围内的点作为扩张终止点
        return turn

    # 变量名简化
    stratedic = {'expand': expand, 'back': back, 'shift': shift, 'attack': attack, 'start': startmode}
    myx, myy = stat['now']['me']['x'], stat['now']['me']['y']
    mydire = stat['now']['me']['direction']
    enemyx, enemyy = stat['now']['enemy']['x'], stat['now']['enemy']['y']
    needShift = False
    # 刷新敌人的纸带
    if stat['now']['fields'][enemyx][enemyy] != stat['now']['enemy']['id']:
        storage['enemyBand'].append((enemyx, enemyy))
    # 敌人回到领地，检查自己领地是否有保存点被吃掉
    elif storage['enemyBand']:
        storage['enemyBand'].append((enemyx, enemyy))
        reBounder(stat, storage, False)
        storage['enemyBand'].clear()
    # 刷新自己的纸带
    if stat['now']['fields'][myx][myy] != stat['now']['me']['id']:
        storage['meBand'].append((myx, myy))
    # 自己回到领地，更新自己领地边界，如果不attack则要领地内shift
    elif storage['meBand']:
        storage['meBand'].clear()
        storage['unsaveBounder'].append((myx, myy))
        reBounder(stat, storage, True)
        storage['strategy'] = {'name': 'Yes'}
        needShift = True
    # back和attack模式有最高优先级
    if storage['strategy']['name'] in ('back', 'attack'):
        turn = stratedic[storage['strategy']['name']](stat, storage)
    else:
        finish = False
        enmToField, enmBackp = None, None
        # 检查是否自己有危险，可能要临时返回
        if storage['meBand']:
            meToField, backEndp = fdistance(stat, (myx, myy),
                                            stat['now']['me']['id'], 'weak', mydire)
            enmToMe = min(bdistance((enemyx, enemyy), stat['now']['enemy']['direction'],
                                    storage['meBand'], (myx, myy))[0],
                          ppdistance((enemyx, enemyy), backEndp))  # 敌人杀死我方的最短距离（直接攻击纸带或者在我方扩张终止点拦截）
            # 简单判断中途拦截可能性
            if myx < enemyx < backEndp[0] or backEndp[0] < enemyx < myx:  # 若水平方向上敌方在我方纸卷和扩张终止点之间
                enmToMe = min(enmToMe, max(abs(enemyy - myy), abs(enemyy - backEndp[1])) - 1)  # 则沿竖直方向拦截
            if myy < enemyy < backEndp[1] or backEndp[1] < enemyy < myy:  # 若竖直方向上敌方在我方纸卷和扩张终止点之间
                enmToMe = min(enmToMe, max(abs(enemyx - myx), abs(enemyx - backEndp[0])) - 1)  # 则沿水平方向拦截
            if meToField + 2 >= enmToMe:  # 发现有被拦截的可能
                turn = back(stat, storage, backEndp)  # 立即返回
                finish = True
            # 防止敌人扩充领地使自己离领地距离突然变远
            elif storage['enemyBand'] and fdistance(stat, backEndp,
                                                    stat['now']['enemy']['id'], 'No', maxdeep=4)[
                0] < 3:  # 发现敌方有侵占我方领地的可能
                enmToField, enmBackp = fdistance(stat, (enemyx, enemyy),
                                                 stat['now']['enemy']['id'], 'No')
                if ppdistance(enmBackp, backEndp) < 30 and \
                        meToField + 3 >= enmToField:  # 发现敌方可能比我方先扩充完领地
                    turn = back(stat, storage, backEndp)  # 立即返回
                    finish = True
        # 检查敌方是否暴露弱点可以进攻
        if not finish and storage['enemyBand']:
            if enmToField is None:
                enmToField, enmBackp = fdistance(stat, (enemyx, enemyy),
                                                 stat['now']['enemy']['id'], 'No')  # 敌方回领地的最短距离
            meToEnm, enmWeakp = bdistance((myx, myy), mydire,
                                          storage['enemyBand'], (enemyx, enemyy))  # 我方攻击敌方纸带的最短距离
            if meToEnm < enmToField:  # 发现在地方回到领地之前我方可以攻击到敌方纸带
                turn = attack(stat, storage, enmWeakp)  # 直接攻击
                finish = True
            # 敌方在自己领地，尝试拦截
            elif (not storage['meBand']) and stat['now']['fields'] \
                    [enemyx][enemyy] == stat['now']['me']['id']:
                meToEnm = min(meToEnm, ppdistance((myx, myy), enmBackp))  # 最短拦截距离
                # 原理与敌方拦截我方相同
                if enemyx < myx < enmBackp[0] or enmBackp[0] < myx < enemyx:
                    meToEnm = min(meToEnm, (abs(myy - enemyy) + abs(myy - enmBackp[1])) // 2)
                if enemyy < myy < enmBackp[1] or enmBackp[1] < myy < enemyy:
                    meToEnm = min(meToEnm, (abs(myx - enemyx) + abs(myx - enmBackp[0])) // 2)
                if meToEnm + 1 < enmToField:  # 发现敌方回到领地之前可以成功拦截
                    turn = attack(stat, storage, enmWeakp)  # 直接攻击
                    finish = True
        # 以上都不成立，照常活动
        if not finish:
            # 刚回到自己领地，要shift
            if needShift:
                turn = shift(stat, storage)
            else:
                turn = stratedic[storage['strategy']['name']](stat, storage)
    if turn[0] in ('L', 'R'):
        storage['lastturn'] = turn
    return turn


def load(stat, storage):
    # storage['bounder']记录重要的自己领地边界坐标
    storage['bounder'] = set()
    # 记录当前策略及信息
    storage['strategy'] = {'name': 'start'}
    # 记录上次转向的方向
    storage['lastturn'] = 'S'
    # 记录未储存的记录节点（边界点），为expand和back模式暂存的
    storage['unsaveBounder'] = []
    # 记录自己和敌方的纸带
    storage['enemyBand'] = []
    storage['meBand'] = []
    # 判断自己攻击应主动还是被动，如果两者相距为奇数则可主动
    storage['attackActive'] = False
