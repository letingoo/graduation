class Particle:

    # position -> 粒子的位置  数组类型
    # speed -> 粒子的速度     数组类型
    # bestFit -> 粒子自身最佳目标函数值
    # worstFit  -> 粒子自身最差目标函数值
    # bestPosition  -> 粒子自身最佳目标函数值对应的位置
    # worstPosition -> 粒子自身最差目标函数值对应的位置

    def __init__(self, position, speed, fit):
        self.position = position
        self.fit = fit
        self.speed = speed
        self.bestFit = fit
        self.worstFit = fit
        self.bestPosition = position
        self.worstPosition = []


    # 更新速度
    def updateSpeed(self, speed):
        self.speed = speed

    # 更新位置
    def updatePosition(self, newPosition):
        self.position = newPosition

    # 更新速度
    def updateSpeed(self, speed):
        self.speed = speed

    # 更新适应度函数
    def updateFit(self, fit):
        if fit < self.bestFit:
            self.bestFit = fit
            self.bestPosition = self.position


    def getSpeed(self):
        return self.speed

    def getPosition(self):
        return self.position

    def getBestPosition(self):
        return self.bestPosition

