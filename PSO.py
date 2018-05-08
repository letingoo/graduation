import numpy as np
import ServiceSimulate
import random
import Particle
import math

# 粒子群列表
particles = []

# 粒子群数量
PARTICLE_NUM = 40

# 最大迭代次数
MAX_TIMES = 200

# SIMULATE
simulate = ServiceSimulate.ServiceSimulate()

# 全局最优粒子位置和其目标函数
bestFit = 100
bestPosition = []


# 全局最差粒子位置和其目标函数
worstFit = 0
worstPosition = []



# 粒子群算法参数
W = 1
C1 = 2
C2 = 2


D_HIGH = 0.6
D_LOW = 0.4




def init():
    global bestFit
    global worstFit
    taskNum = simulate.tasksSize()

    for i in range(PARTICLE_NUM):
        positionList = []
        for j in range(taskNum):
            low = simulate.getTasks(j).getStartTime()
            high = simulate.getTasks(j).getLastTime()
            positionList.append(random.randint(low, high))

        # 初始化位置
        position = np.array(positionList)
        speed = position // 2
        particles.append(Particle.Particle(position, speed, calculateTargetFunc(position)))
        nowTargetFunc = calculateTargetFunc(position)
        if nowTargetFunc < bestFit:
            bestFit = nowTargetFunc
            global bestPosition
            bestPosition = position

        if nowTargetFunc > worstFit:
            worstFit = nowTargetFunc
            global worstPosition
            worstPosition = position


# 计算适应度函数
def calculateTargetFunc(position):
    total = 0

    for i in range(len(position)):
        total += position[i] - simulate.getTasks(i).getStartTime()

    total = total + simulate.penaltyFunction(position)

    return total / simulate.tasksSize()



# 更新粒子位置，注意处理上下限问题
def updatePosition(particle):
    pos = particle.getPosition()
    speed = particle.getSpeed()
    newPos = pos + speed

    taskLen = simulate.tasksSize()
    for i in range(taskLen):
        if newPos[i] <= simulate.getTasks(i).getStartTime():
            newPos[i] = simulate.getTasks(i).getStartTime()

        if newPos[i] >= simulate.getTasks(i).getLastTime():
            newPos[i] = simulate.getTasks(i).getLastTime()

    particle.updatePosition(newPos)




# 基础粒子群
def mainPart():

    global bestFit, worstFit
    global worstPosition, bestPosition
    for i in range(MAX_TIMES):

        diversity = calculateDiversity()
        if diversity > D_HIGH:
            for p in particles:
                newSpeed = calculateSpeed(p)
                p.updateSpeed(newSpeed)
                updatePosition(p)
                newFit = calculateTargetFunc(p.getPosition())
                if newFit <= bestFit:
                    bestFit = newFit
                    bestPosition = p.getPosition()

                if newFit >= worstFit:
                    worstFit = newFit
                    worstPosition = p.getPosition()

                p.updateFit(newFit)

        elif diversity < D_LOW:
            for p in particles:
                newSpeed = calculateSpeedExclude(p)
                p.updateSpeed(newSpeed)
                updatePosition(p)
                newFit = calculateTargetFunc(p.getPosition())
                if newFit <= bestFit:
                    bestFit = newFit
                    bestPosition = p.getPosition()

                if newFit >= worstFit:
                    worstFit = newFit
                    worstPosition = p.getPosition()

                p.updateFit(newFit)

        else:
            for p in particles:
                speed = p.speed
                p.updateSpeed(speed)
                updatePosition(p)
                newFit = calculateTargetFunc(p.getPosition())
                if newFit <= bestFit:
                    bestFit = newFit
                    bestPosition = p.getPosition()

                if newFit >= worstFit:
                    worstFit = newFit
                    worstPosition = p.getPosition()

                p.updateFit(newFit)

        print(bestFit)


# 粒子群算法计算速度,吸引
def calculateSpeed(particle):
    speed = particle.getSpeed()
    position = particle.getPosition()
    singleBestPos = particle.getBestPosition()

    part1 = np.floor(W * speed)
    part2 = np.floor(C1 * random.random() * (singleBestPos - position))
    part3 = np.floor(C2 * random.random() * (bestPosition - position))
    newSpeed = part1 + part2 + part3
    return newSpeed


# 粒子群算法计算速度，排斥操作
def calculateSpeedExclude(particle):
    speed = particle.getSpeed()
    position = particle.getPosition()
    singleWorstPos = particle.worstPosition

    part1 = np.floor(W * speed)
    part2 = np.floor(C1 * random.random() * (singleWorstPos - position))
    part3 = np.floor(C2 * random.random() * (worstPosition - position))
    newSpeed = part1 - part2 - part3
    return newSpeed








# 计算种群多样性
def calculateDiversity():
    P = len(particles)          # 种群数量

    L = 0;                      # 搜索空间对角线长度
    for i in range(simulate.tasksSize()):
        t = simulate.getTasks(i)
        L = L + pow(t.lastStartTime - t.expectedStartTime, 2)

    L = math.sqrt(L)



    length = simulate.tasksSize()
    initS = []
    for i in range(length):
        initS.append(0)


    S = np.array(initS)         #  粒子的平均向量
    for particle in particles:
        S = S + particle.position
    S = S / P


    sum = 0
    for particle in particles:
        subSum = 0
        for i in range(length):
            num = particle.position[i]
            subSum = subSum + pow(num - S[i], 2)

        sum = sum + math.sqrt(subSum)

    return sum / (L * P)






init()

testPos = [1, 4, 3, 1, 2, 10, 10, 10, 18, 19, 10, 8, 2]
simulate.checkBussinessConflict(testPos)

print("done")
mainPart()
print(bestPosition)

print( simulate.checkBussinessConflict(bestPosition) )