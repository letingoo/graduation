class Task:


    #jID  --> 检修任务ID
    #equipLabel --> 检修设备名称
    #expectedStartTime  --> 检修设备期待开始时间
    #lastStartTime  --> 检修设备最晚开始时间
    #type  -->  检修类型，分两种，分别是不可调整时间和可以调整时间
    #costTime --> 检修花费时间


    def __init__(self, jID, equipLabel, expectedStartTime, lastStartTime, type, costTime):
        self.jID = jID
        self.equipLabel = equipLabel
        self.expectedStartTime = expectedStartTime
        self.lastStartTime = lastStartTime
        self.type = type
        self.costTime = costTime



    def getStartTime(self):
        return self.expectedStartTime

    def getLastTime(self):
        return self.lastStartTime

    def getCostTime(self):
        return self.costTime


    def getEquipLabel(self):
        return self.equipLabel
