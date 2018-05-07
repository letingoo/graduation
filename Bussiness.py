class Bussiness:


    # name --> 业务id
    # mainRoute --> 业务主用路由
    # backRoute --> 业务备用路由
    # changed --> 业务的状态
    #             0——主备路由均正常使用
    #             1——备用路由被检修
    #             2——主用路由被检修，业务已经被切换至备用路由


    def __init__(self, name, mainRoute, backRoute):
        self.name = name
        self.mainRoute = mainRoute.split('-')
        self.backRoute = backRoute.split('-')
        self.changed = 0


    def changeRoute(self, changed):
        self.changed = changed
