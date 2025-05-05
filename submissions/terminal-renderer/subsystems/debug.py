class Debug:
    def __init__(self):
        self.log = []
    def post(self, data):
        self.log.append(data)
    def detail(self):
        print("\033[0m" + "Debug:")
        for item in self.log:
            print(item)
        self.log.clear()