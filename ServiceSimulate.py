import pymysql.cursors
import Equip
import Bussiness
import Task
import numpy as np

class ServiceSimulate:



    # equips --> 设备Map
    # initEquips --> 原始设备Map，因为设备承载业务的信息会一直改变
    # bussinessList --> 业务列表Map
    # tasks --> 检修任务列表

    # RESOURCE_LIMIT --> 资源约束






    def __init__(self):

        self.equips = {}
        self.initEquips = {}
        self.bussinessList = {}
        self.tasks = []
        self.RESOURCE_LIMIT = 4


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
            self.initEquips[equipLabel] = equip

        sql = 'select bussiness_label, main_route, back_route from bussiness'
        cursor.execute(sql)
        result = cursor.fetchall()
        for row in result:
            bussinessName = row['bussiness_label']
            self.bussinessList[bussinessName] = Bussiness.Bussiness(bussinessName, row['main_route'], row['back_route'])


        sql = 'select equipLabel, jID, expectedStartTime, lastStartTime, type, costTime from task'
        cursor.execute(sql)
        result = cursor.fetchall()
        for row in result:
            if row['type'] == 1:
                continue
            self.tasks.append(Task.Task(row['jID'], row['equipLabel'],
                                   row['expectedStartTime'], row['lastStartTime'], row['type'], row['costTime']))

        cursor.close()
        connection.close()



    # 构造业务和设备对应模型
    def analyseBussinessEquip(self):
        for name,bussiness in self.bussinessList.items():
            for equip in bussiness.mainRoute:
                self.equips[equip].mainBussiness.append(bussiness.name)
                self.initEquips[equip].mainBussiness.append(bussiness.name)

            for equip in bussiness.backRoute:
                self.equips[equip].backBussiness.append(bussiness.name)
                self.initEquips[equip].backBussiness.append(bussiness.name)



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


        for bussiness_name in mainBussinessList:

            bussiness = self.bussinessList[bussiness_name]
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

        for bussiness_name in backBussinessList:
            bussiness = self.bussinessList[bussiness_name]
            for e in bussiness.backRoute:
                e_backBussiness = self.equips[e].backBussiness
                e_backBussiness.remove(bussiness.name)

            bussiness.changeRoute(1)

        return True



    # 检修恢复
    def doRecover(self, action):

        try:
            equip = action.equipLabel
            self.equips[equip].state = 0
            # 先恢复主用路由的业务
            mainBussinessList = self.initEquips[equip].getMainBussiness()
            for bussinessName in mainBussinessList:
                mainRoute = self.bussinessList[bussinessName].mainRoute
                flag = True
                for e in mainRoute:
                    if self.equips[e].state == 1:
                        flag = False
                        break

                # 将业务切换至主用路由
                if flag:

                    # 先从备用路由上撤出
                    for name,e2 in self.equips.items():
                        if e2.mainBussiness.index(bussinessName) >= 0:
                            e2.mainBussiness.remove(bussinessName)
                            e2.backBussiness.append(bussinessName)

                    # 再切换到主用路由上
                    for e2 in mainRoute:
                        e2.mainBussiness.append(bussinessName)


                    self.bussinessList[bussinessName].changed = 0


            # 再恢复备用路由的业务
            backBussinessList = self.initEquips[equip].backBussiness
            for bussinessName in backBussinessList:
                backRoute = self.bussinessList[bussinessName].backRoute
                flag = True
                for e in backRoute:
                    if self.equips[e].state == 1:
                        flag = False
                        break

                # 该业务的备用路由变为可用
                if flag:
                    for e2 in backRoute:
                        self.equips[e2].backBussiness.append(bussinessName)

                    self.bussinessList[bussinessName].changed = 0

        except ValueError:
            print("err")


    # 检查是否有资源冲突
    def checkResourceConflict(self, position):
        start = position
        end = start + self.getCostArr()

        actions = []
        for i in range(start.size):
            startAction = Action(0, self.getTasks(i).getEquipLabel(), start[i])
            actions.append(startAction)

        for i in range(end.size):
            endAction = Action(1, self.getTasks(i).getEquipLabel(), end[i])
            actions.append(endAction)


        actions.sort(key=lambda a:a.time, reverse=False)
        count = 0
        for ac in actions:
            if ac.isRepair == 1:
                count = count - 1
            else:
                count = count + 1
                if count > self.RESOURCE_LIMIT:
                    return False

        return True




    # 检查是否有业务中断冲突
    def checkBussinessConflict(self, position):
        start = position
        length = len(position)
        end = start + self.getCostArr()[:length]

        actions = []
        for i in range(len(start)):
            startAction = Action(0, self.getTasks(i).getEquipLabel(), start[i])
            actions.append(startAction)

        for i in range(len(end)):
            endAction = Action(1, self.getTasks(i).getEquipLabel(), end[i])
            actions.append(endAction)

        # 对检修操作进行排序，排序先按操作的时间排序，时间一致时恢复操作是在检修操作之前
        actions.sort(key=lambda a:a.time, reverse=False)

        for ac in actions:
            if ac.isRepair == 0:
                if self.doRepair(ac) == False:
                    return False

            else:
                self.doRecover(ac)

        return True




    # 罚函数
    def penaltyFunction(self, position):


        # 先恢复原状
        self.equips = {}

        for name, e in self.initEquips.items():
            e_name = e.name
            self.equips[e_name] = Equip.Equip(e_name)
            self.equips[e_name].state = 0

            mainBussinessList = e.mainBussiness
            for b in mainBussinessList:
                self.equips[e_name].mainBussiness.append(b)

            backBussinessList = e.backBussiness
            for b in backBussinessList:
                self.equips[e_name].backBussiness.append(b)



        penalty = 0
        if self.checkResourceConflict(position) == False:
            penalty = penalty + 50


        if self.checkBussinessConflict(position) == False:
            penalty = penalty + 50




        return penalty




# 检修的操作
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