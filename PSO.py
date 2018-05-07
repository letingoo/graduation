import numpy as np
import ServiceSimulate
import random
import Particle

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


# 粒子群算法参数
W = 1
C1 = 2
C2 = 2



def init():
    global bestFit
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
        if calculateTargetFunc(position) < bestFit:
            bestFit = calculateTargetFunc(position)
            global bestPosition
            bestPosition = position


# 计算适应度函数
def calculateTargetFunc(position):
    total = 0

    for i in range(len(position)):
        total += position[i] - simulate.getTasks(i).getStartTime()

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

    global bestFit
    for i in range(MAX_TIMES):

        for p in particles:
            newSpeed = calculateSpeed(p)
            p.updateSpeed(newSpeed)
            updatePosition(p)
            newFit = calculateTargetFunc(p.getPosition())
            if newFit <= bestFit:
                bestFit = newFit
                global bestPosition
                bestPosition = p.getPosition()

            p.updateFit(newFit)

        print(bestFit)


# 粒子群算法计算速度
def calculateSpeed(particle):
    speed = particle.getSpeed()
    position = particle.getPosition()
    singleBestPos = particle.getBestPosition()

    part1 = np.floor(W * speed)
    part2 = np.floor(C1 * random.random() * (singleBestPos - position))
    part3 = np.floor(C2 * random.random() * (bestPosition - position))
    newSpeed = part1 + part2 + part3
    return newSpeed




init()
print("done")
mainPart()
print(bestPosition)

print( simulate.checkBussinessConflict(bestPosition) )