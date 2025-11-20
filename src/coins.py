from cmu_graphics import *
from Collision import HitBox
import hitBoxTest
import os
import random
def absPath(filename):
    baseDir = os.path.dirname(os.path.abspath(__file__))
    relativePath = os.path.join('Images', filename)
    return os.path.normpath(os.path.join(baseDir, relativePath))

class Coin(HitBox):
    def __init__(self, cx, cy):
        self.size = 35
        # super().__init__((cx-self.size//2, cy-self.size//2), 
        #                  (cx+self.size//2, cy-self.size//2), 
        #                  (cx+self.size//2, cy+self.size//2), 
        #                  (cx-self.size//2, cy+self.size//2))
        super().__init__(*hitBoxTest.getConvexHull("Coin-0.png", 
                                                  (cx, cy), self.size, 
                                                  self.size, 0))
        self.cx = cx
        self.cy = cy


class CoinCollection:
    def __init__(self):
        self.size = 35
        self.coins = []
        self.totalCoins = 0
        self.k = random.randint(0, 4)

    def drawCoins(self, i):
        for coin in self.coins:
            drawImage(f'{absPath("Coin")}-{45*(i+self.k) % 270}.png', 
                      coin.cx, 
                      coin.cy, 
                      width=self.size, height=self.size)
            # drawPolygon(*hitBoxTest.fancyFlattenEdgeList(coin.polygon))
            
    def addDesign(self, choice, x, y, n=10):
        designs = {
            1: lambda: self.hline(x, y, n),
            2: lambda: self.vline(x, y, n),
            3: lambda: self.diag(x, y, n)
        }
        designs[choice]()


    def removeCoin(self, coin):
        if coin in self.coins:
            self.coins.remove(coin)

    #n is number of coins, x,y is starting position of leftmost
    def hline(self, x, y, n): 
        for i in range(n): self.coins.append(Coin(x+i*self.size//1.1, y))

    #n is number of coins, x,y is starting position of leftmost
    def vline(self, x, y, n): 
        for i in range(n): self.coins.append(Coin(x, y+i*self.size//1.1))

    def diag(self, x, y, n):
        for i in range(n): 
            self.coins.append(Coin(x+y+i*self.size//1.1, y+i*self.size//1.1))

    #Remove any coins off the game
    def updateCoins(self, rate, Barry):
        temp = []
        for coin in self.coins:
            #Check if collide with Barry
            if coin.checkCollision(Barry): 
                self.totalCoins += 1
                continue

            #If goes off screen remove
            if coin.cx >-self.size/15:
                coin.cx -= rate
                temp.append(coin)
            for i in range(len(coin.polygon)):
                x, y = coin.polygon[i]
                coin.polygon[i] = (x - rate, y)
        self.coins = temp