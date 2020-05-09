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
grid = []
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
            self.maxsize = random.randint(4,10)
            if random.randint(0,4) == 0:
                self.maxsize += random.randint(10,20)
        else:
            self.maxsize = maxsize

        if color is None:
            self.color = (random.randint(60,255),random.randint(60,255),random.randint(60,255))
        else:
            self.color = color

        if speed is None:
            self.speed = random.randint(20,500)
        else:
            self.speed = speed

        grid_lock.acquire()
        while True:
            startx = random.randint(0,cells_wide-1)  # random position to start
            starty = random.randint(0,cells_high-1)
            if grid[startx][starty] is None:
                break
        grid[startx][starty] = self.color  # set init color,placeholder占位
        # print(grid[startx][starty])
        # print(grid[startx])
        grid_lock.release()

        self.body = [{'x':startx,'y':starty}]   # worm body
        self.direction = random.choice((up,down,left,right))    # worm random direction

    def run(self):
        while True:
            if not worms_running:
                return
            if random.randint(0,100) < 20:  #在移动的每一步上，有20%的机会虫子会随机地改变方向。
                self.direction = random.choice((up,down,left,right))

            grid_lock.acquire()
            nextx,nexty = self.getNextPosition()
            if nextx in (-1,cells_wide) or nexty in (-1,cells_high) or grid[nextx][nexty] is not None:
                self.direction = self.getNewDirection()

                if self.direction is None:
                    self.body.reverse()
                    self.direction = self.getNewDirection()
                if self.direction is not None:
                    nextx,nexty = self.getNextPosition()

            if self.direction is not None:
                grid[nextx][nexty] = self.color
                self.body.insert(0,{'x':nextx,'y':nexty})

                if len(self.body) > self.maxsize:
                    grid[self.body[butt]['x']][self.body[butt]['y']] = None
                    del self.body[butt]
            else:
                self.direction = random.choice((up,down,left,right))
            grid_lock.release()
            pygame.time.wait(self.speed)

    def getNextPosition(self):
        """根据虫头当前的位置和方向，来计算出虫头下一步的x和y坐标"""
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
    global fpsclock, displaysurf

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
    displaysurf = pygame.display.set_mode((windowwidth,windowheight))
    pygame.display.set_caption('Threadworms')

    worms = []
    for i in range(num_worms):
        worms.append(Worm(name='Worm %s' % i))
        worms[-1].start()
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
    displaysurf.fill(bgcolor)
    for x in range(0,windowwidth,cell_size):
        pygame.draw.line(displaysurf,grid_line_color,(x,0),(x,windowheight))
    for y in range(0,windowheight,cell_size):
        pygame.draw.line(displaysurf,grid_line_color,(0,y),(windowwidth,y))

    grid_lock.acquire()
    for x in range(0,cells_wide):
        for y in range(0,cells_high):
            if grid[x][y] is None:
                continue
            color = grid[x][y]
            darkerColor = (max(color[0] - 50,0),max(color[1] - 50,0),max(color[2] - 50,0))
            pygame.draw.rect(displaysurf,darkerColor,(x * cell_size,y*cell_size,cell_size,cell_size))
            pygame.draw.rect(displaysurf,color,(x*cell_size+4,y*cell_size+4,cell_size-8,cell_size-8))
    grid_lock.release()

def setGridSquares(squares,color=(192,192,192)):
    squares = squares.split('\n')
    if squares[0] == '':
        del squares[0]
    if squares[-1] == '':
        del squares[-1]

    grid_lock.acquire()
    for y in range(min(len(squares),cells_high)):
        for x in range(min(len(squares[y]),cells_wide)):
            if squares[y][x] == ' ':
                grid[x][y] = None
            elif squares[y][x] == '.':
                pass
            else:
                grid[x][y] = color
    grid_lock.release()

if __name__ == '__main__':
    main()




