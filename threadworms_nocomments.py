# -*- coding: utf-8 -*-
#! python3

import random,pygame,sys,threading,pprint
from pygame.locals import *

# setting up contants
num_worms = 24  # the number of worms in the grid
fps = 30
cell_size = 20  # how many pixels wide and high each "cell" in the gird is
cells_wide = 32  # how many cells wide the grid is
cells_high = 24  # how many cells high the grid is
grid = []  # ！！！！！核心全局变量grid列表，数值color，数据分3种：空白None，字母固定颜色，worms初始颜色，但多线程数据在变化
for x in range(cells_wide):
    grid.append([None] * cells_high)    # put [None] in all cells

grid_lock = threading.Lock()

white = (255,255,255)
black = (0,0,0)
darkgray = (40,40,40)
bgcolor = black
grid_line_color = darkgray

windowwidth = cell_size * cells_wide
windowheight = cell_size * cells_high

up = 'up'
down = 'down'
left = 'left'
right = 'right'

head = 0    # worm head
butt = -1   # worm butt

# A global variable that the worm threads check to see if they should exit.
worms_running = True

class Worm(threading.Thread):
    def __init__(self, name='worm', maxsize=None, color=None, speed=None):
        threading.Thread.__init__(self)
        # super(Worm,self).__init__()
        self.name = name
        if maxsize is None:
            self.maxsize = random.randint(4,6)
            if random.randint(0,4) == 0:
                self.maxsize += random.randint(3,6)
        else:
            self.maxsize = maxsize

        if color is None:
            self.color = (random.randint(60,255),random.randint(60,255),random.randint(60,255))
        else:
            self.color = color

        if speed is None:
            self.speed = random.randint(10,600)
        else:
            self.speed = speed

        grid_lock.acquire()
        while True:
            # 初始化便进行生成。多线程循环生成初始x，y坐标位置
            startx = random.randint(0,cells_wide-1)  # random init position
            # print(startx)  # 因为多线程，初始生成的随机点位是比网格格数多
            starty = random.randint(0,cells_high-1)
            if grid[startx][starty] is None:  #因为是多线程随机，所以startx和starty的数量会不等，缺少的数据便是None，break跳出
                break

        grid[startx][starty] = self.color  # set init random color,placeholder（占位）每个格子都给了随机颜色
        # print(grid[startx][starty])  # 这里会有24个网格初始赋值了随机颜色
        # print(grid[startx])
        grid_lock.release()


        self.body = [{'x':startx,'y':starty}]   # worm body=head=butt one grid position
        self.direction = random.choice((up,down,left,right))    # worm init random direction

    def run(self):
        while True:
            if not worms_running:
                return
            if random.randint(0,100) < 20:  #在移动的每一步上，有20%的机会虫子会随机地改变方向。
                self.direction = random.choice((up,down,left,right))

            grid_lock.acquire()
            nextx,nexty = self.getNextPosition()  # 往前走一步
            if nextx in (-1,cells_wide) or nexty in (-1,cells_high) or grid[nextx][nexty] is not None:
                # 顶、底、左、右边框或grid被占用，
                self.direction = self.getNewDirection()  # 重新计算方向，赋方向值

                if self.direction is None:  # 返回的方向是None
                    self.body.reverse()  # self.body是一个列表，将列表内的元素翻转
                    self.direction = self.getNewDirection()  # 重新计算方向
                if self.direction is not None:  # 方向有值
                    nextx,nexty = self.getNextPosition()  # 根据方向值计算x，y坐标位置

            if self.direction is not None:
                grid[nextx][nexty] = self.color  # grid赋值颜色，同初始化中的占位颜色值
                self.body.insert(0,{'x':nextx,'y':nexty})  # 往worm body列表的0位(head)插入新的x，y字典位置数值

                if len(self.body) > self.maxsize:
                    grid[self.body[butt]['x']][self.body[butt]['y']] = None  # 将body[butt]占的grid赋值为None
                    del self.body[butt]  # 删除body列表最后一个元素字典，这样worm会始终保持最长长度
            else:
                self.direction = random.choice((up,down,left,right))
            grid_lock.release()
            pygame.time.wait(self.speed)

    def getNextPosition(self):
        """根据虫头当前的位置和方向，来计算并移动虫头下一步的x和y坐标"""
        if self.direction == up:
            nextx = self.body[head]['x']
            nexty = self.body[head]['y'] - 1
        elif self.direction == down:
            nextx = self.body[head]['x']
            nexty = self.body[head]['y'] + 1
        elif self.direction == left:
            nextx = self.body[head]['x'] - 1
            nexty = self.body[head]['y']
        elif self.direction == right:
            nextx = self.body[head]['x'] + 1
            nexty = self.body[head]['y']
        else:
            assert False,'Bad value for self.direction: %s' % self.direction  #断言，爆出方向错误
        return nextx,nexty

    def getNewDirection(self):
        """判断头前后左右格是否被占，来获得新的移动方向"""
        x = self.body[head]['x']  # [{'x': 6, 'y': 2}, {'x': 7, 'y': 2}, {'x': 8, 'y': 2}]
        # [head]=0,对应的是头，[body]=1...对应的是身子，[butt]=-1对应的是屁股
        y = self.body[head]['y']
        # print(self.body)

        newDirection = []
        if y - 1 not in (-1,cells_high) and grid[x][y-1] is None:
            # (-1,cells_high)对应的是顶和底部边界，grid[x][y-1]对应的是y轴上一格是不是none
            newDirection.append(up)
        if y + 1 not in (-1,cells_high) and grid[x][y+1] is None:
            newDirection.append(down)
        if x - 1 not in (-1,cells_wide) and grid[x-1][y] is None:
            newDirection.append(left)
        if x + 1 not in (-1,cells_wide) and grid[x+1][y] is None:
            newDirection.append(right)

        if newDirection == []:
            return None     # None表示没有地方移动

        return random.choice(newDirection)  # 对可以朝向的方向在做随机

def main():
    """main()函数是用于测试这些类和函数功能的，其他类和函数可以被import出去使用。"""
    global fpsclock, screen

    squares = """
...........................
...........................
...........................
.H..H..EEE..L....L.....OO..
.H..H..E....L....L....O..O.
.HHHH..EE...L....L....O..O.
.H..H..E....L....L....O..O.
.H..H..EEE..LLL..LLL...OO..
...........................
.W.....W...OO...RRR..MM.MM.
.W.....W..O..O..R.R..M.M.M.
.W..W..W..O..O..RR...M.M.M.
.W..W..W..O..O..R.R..M...M.
..WW.WW....OO...R.R..M...M.
...........................
...........................
"""
    setGridSquares(squares)

    pygame.init()
    fpsclock = pygame.time.Clock()
    screen = pygame.display.set_mode((windowwidth, windowheight))
    pygame.display.set_caption('Threadworms')

    worms = []   # worm虫的列表，循环限定数量进行start（）
    for i in range(num_worms):
        worms.append(Worm(name='Worm %s' % i))
        worms[-1].start()   # .start（）启动类Worm这个多线程进程！！！
    while True:
        handleEvents()
        drawGrid()

        pygame.display.update()
        fpsclock.tick(fps)

def handleEvents():
    global worms_running
    for event in pygame.event.get():
        if (event.type == QUIT) or (event.type == KEYDOWN and event.key == K_ESCAPE):
            worms_running = False
            pygame.quit()
            sys.exit()

def drawGrid():
    """添加网格，描绘worm每个格的颜色"""
    screen.fill(bgcolor)  # 绘制bg
    for x in range(0,windowwidth,cell_size):
        pygame.draw.line(screen, grid_line_color, (x, 0), (x, windowheight))  # 绘制竖条
    for y in range(0,windowheight,cell_size):
        pygame.draw.line(screen, grid_line_color, (0, y), (windowwidth, y))  # 绘制横条

    # 绘制worm和字体格子上的颜色
    grid_lock.acquire()
    for x in range(0,cells_wide):
        for y in range(0,cells_high):
            if grid[x][y] is None:  # ！！！grid空白的格子颜色是None，continue跳过，那么剩下的都将是固定的字母和移动的worms
                continue
            color = grid[x][y]  # 通过遍历x，y来读取grid下面的颜色
            # print(color)
            # color = (168,0,65)
            darkerColor = (max(color[0] - 50,0),max(color[1] - 50,0),max(color[2] - 50,0))
            # print(darkerColor)
            pygame.draw.rect(screen, darkerColor, (x * cell_size, y * cell_size, cell_size, cell_size))
            pygame.draw.rect(screen, color, (x * cell_size + 4, y * cell_size + 4, cell_size - 8, cell_size - 8))
    grid_lock.release()

def setGridSquares(squares,color=(192,192,192)):
    squares = squares.split('\n')
    print(squares)
    # print(min(len(squares),cells_high))
    if squares[0] == '':
        del squares[0]  # 删掉开头''
    if squares[-1] == '':
        del squares[-1]  # 删掉结尾''

    grid_lock.acquire()
    for y in range(min(len(squares),cells_high)):  # 先行后列！！！使用squares有多少行作为range数位
        for x in range(min(len(squares[y]),cells_wide)):  # 这里设置了求得squares一行有多少位，作为range的数位
            # if squares[y][x] == ' ':  # 保险代码，上面已经删除开头结尾''空数据了
            #     grid[x][y] = None
            if squares[y][x] == '.':  # 表格里面数据是'.'，就pass跳过，去掉.以外的都付统一颜色，
                pass
            elif squares[y][x] == 'H':   # 这里也可以一直elif下去，== 'H'，赋值颜色
                grid[x][y] = (110,198,50)
            else:
                grid[x][y] = color  # 赋值灰色
    grid_lock.release()

if __name__ == '__main__':
    main()
#  用于对当前页面上的类或是Function进行测试运行，可以将其写在main（）Function下面，这样在导入import至其他代码页中时，
#  main（）Function是不会允许的。




