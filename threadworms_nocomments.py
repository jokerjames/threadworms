import random,pygame,sys,threading
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
    def __init__(self,name='worm',maxsize=None,color=None,speed=None):
        threading.Thread.__init__(self)
        # super(Worm,self).__init__()
        self.name = name
        if maxsize is None:
            self.maxsize = random.randint(4,10)
            if random(0,4) == 0:
                self.maxsize += random.randint(10,20)
        else:
            self.maxsize = maxsize

        if color is None:
            self.color(random.randint(60,255),random.randint(60,255),random.randint(60,255))
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
        grid[startx][starty] = self.color  # set init color
        grid_lock.release()

        self.body = [{'x':startx,'y':starty}]   # worm body
        self.direction = random.choice((up,down,left,right))    # worm random direction

    def run(self):
        while True:
            if not worms_running:
                return
            if random.randint(0,100) < 20:
                self.direction = random.choice((up,down,left,right))

            grid_lock.acquire()
            nextx,nexty = self.getNextPosition()
            if nextx in (-1,cells_wide) or nexty in (-1,cells_high) or grid[nextx][nexty] is not None:
                self.direction = self.getNewDirection()

                if self.direction is None:
                    self.body.reverse()
                    self.direction = self.getNewPosition()
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
            assert False,'Bad value for self.direction: %s' % self.direction
        return nextx,nexty






