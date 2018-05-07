import pymysql.cursors
import Equip
import Bussiness
import Task
import numpy as np

class ServiceSimulate:



    # equips --> 设备Map
    # bussinessList --> 业务列表
    # tasks --> 检修任务列表


    def __init__(self):

        self.equips = {}
        self.bussinessList = []
        self.tasks = []

        self.readDataFromDB()
        self.analyseBussinessEquip()

        print("init done")



    # 从数据库中读取数据
    def readDataFromDB(self):
        connection = pymysql.connect(host='114.215.159.226', port=3306, user='root',
                                     password='931011', db='graduation_pro', charset='utf8',
                                     cursorclass=pymysql.cursors.DictCursor)

        cursor = connection.cursor()

        sql = 'select equipLabel from equip'

        cursor.execute(sql)

        result = cursor.fetchall()
        for row in result:
            equipLabel = row['equipLabel']
            equip = Equip.Equip(equipLabel)
            self.equips[equipLabel] = equip

        sql = 'select bussiness_label, main_route, back_route from bussiness'
        cursor.execute(sql)
        result = cursor.fetchall()
        for row in result:
            self.bussinessList.append(Bussiness.Bussiness(row['bussiness_label'], row['main_route'], row['back_route']))

        sql = 'select equipLabel, jID, expectedStartTime, lastStartTime, type, costTime from task'
        cursor.execute(sql)
        result = cursor.fetchall()
        for row in result:
            self.tasks.append(Task.Task(row['jID'], row['equipLabel'],
                                   row['expectedStartTime'], row['lastStartTime'], row['type'], row['costTime']))

        cursor.close()
        connection.close()



    # 构造业务和设备对应模型
    def analyseBussinessEquip(self):
        for bussiness in self.bussinessList:
            for equip in bussiness.mainRoute:
                self.equips[equip].mainBussiness.append(bussiness.name)

            for equip in bussiness.backRoute:
                self.equips[equip].backBussiness.append(bussiness.name)




    def equipSize(self):
        return len(self.equips)


    def tasksSize(self):
        return len(self.tasks)


    def getTasks(self, index):
        return self.tasks[index]



    def getCostArr(self):
        theCost = []
        for task in self.tasks:
            theCost.append(task.getCostTime())

        return np.array(theCost)



    # 执行检修
    def doRepair(self, action):
        equip = action.equipLabel

        # 设备上承载的主用路由业务
        mainBussinessList = self.equips[equip].getMainBussiness()


        for bussiness in mainBussinessList:

            # 先判断可否转移路由
            # 只有一条路由，检修它当然会冲突
            if bussiness.changed == 1 or bussiness.changed == 2:
                return False


            # 先更改主用路由经过该点的业务
            for e in bussiness.mainRoute:
                e_mainBussiness = self.equips[e].mainBussiness
                e_mainBussiness.remove(bussiness.name)


            for e in bussiness.backRoute:
                e_mainBussiness = self.equips[e].mainBussiness
                e_mainBussiness.append(bussiness.name)

                e_backBussiness = self.equips[e].backBussiness
                e_backBussiness.remove(bussiness.name)


            bussiness.changeRoute(2)



        # 更改备用路由
        backBussinessList = self.equips[equip].getBackBussiness()

        for bussiness in backBussinessList:

            for e in bussiness.backRoute:
                e_backBussiness = self.equips[e].backBussiness
                e_backBussiness.remove(bussiness.name)

            bussiness.changeRoute(1)



    # 检修恢复
    def doRecover(self, action):
        equip = action.equipLabel
        mainBussinessList = self.equips[equip].getMainBussiness()





    def checkBussinessConflict(self, position):
        start = position
        end = start + self.getCostArr()

        actions = []
        for i in range(start.size):
            startAction = Action(0, self.getTasks(i).getEquipLabel(), start[i])
            actions.append(startAction)

        for i in range(end.size):
            endAction = Action(1, self.getTasks(i).getEquipLabel(), end[i])
            actions.append(endAction)

        # 对检修操作进行排序，排序先按操作的时间排序，时间一致时恢复操作是在检修操作之前
        actions.sort(key=lambda a:a.time, reverse=False)

        for ac in actions:



# 行动
class Action:

    # isRepait --> 开始检修或者结束检修,   0代表开始 1代表结束
    # equipLabel --> 指定的设备
    # time --> 时间

    def __init__(self, isRepair, equipLabel, time):
        self.isRepair = isRepair
        self.equipLabel = equipLabel
        self.time = time


    def __cmp__(self, other):
        if self.time < other.time:
            return -1

        elif self.time > other.time:
            return 1

        else:
            return self.isRepair - other.isRepair