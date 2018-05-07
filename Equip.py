class Equip:


    # name --> 设备ID
    # mainBussiness --> 主用路由受该设备影响的业务
    # backBussiness --> 备用路由受该设备影响的业务
    # state --> 设备的状态，是正常运行还是被检修。0代表正常运行，1代表被检修

    def __init__(self, name):
        self.name = name
        self.mainBussiness = []
        self.backBussiness = []
        self.state = 0


    def getMainBussiness(self):
        return self.mainBussiness


    def getBackBussiness(self):
        return self.backBussiness