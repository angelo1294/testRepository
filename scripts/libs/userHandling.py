import sys
from restRequests import iteUserHandling, getToken, userLogout


class User:
    def __init__(self, velo, ite, users, username='qatestuser', mode='1111'):
        self.switcher = {
            '0000': self.default,
            '0001': self.first,
            '0010': self.second,
            '0011': self.third,
            '0100': self.fourth,
            '0101': self.default,
            '0110': self.sixth,
            '0111': self.seventh,
            '1000': self.eighth,
            '1001': self.ninth,
            '1010': self.tenth,
            '1011': self.eleventh,
            '1100': self.default,
            '1101': self.default,
            '1110': self.fourteenth,
            '1111': self.fifteenth
        }
        self.username = username
        if len(mode) > 4:
            print('Bad parameters were given for execution')
            sys.exit(1)
        elif len(mode) < 4:
            mode = mode + '0' * (4 - len(mode))
        self.switcher[mode](velo, ite, users)

    #####################################################################
    ###Base functions for create users, login, logout and remove users###
    #####################################################################
    def createUsers(self, ite, users):
        failTest = 0
        for index in range(0, users):
            name = self.username + str(index)
            result = iteUserHandling(ite=ite, mode='update', userid=name, name=name, password=name)
            if not result:
                print('User ' + name + ' has not been created')
                failTest = 1
        return failTest

    def authenticateUsers(self, velo, users):
        failTest = 0
        for index in range(0, users):
            name = self.username + str(index)
            token = getToken(velo=velo, username=name, password=name)
            if not token:
                print('Login failed for user ' + name)
                failTest = 1
        return failTest

    def logoutUsers(self, velo, users):
        failTest = 0
        for index in range(0, users):
            name = self.username + str(index)
            token = getToken(velo=velo, username=name, password=name)
            if not token:
                print('Login failed for user ' + name)
                failTest = 1
            result = userLogout(velo=velo, token=token)
            if not result:
                print('Logout failed for user ' + name)
                failTest = 1
        return failTest

    def removeUsers(self, ite, users):
        failTest = 0
        for index in range(0, users):
            name = self.username + str(index)
            result = iteUserHandling(ite=ite, mode='delete', userid=name, name=name, password=name)
            if not result:
                print('User ' + name + ' has not been deleted')
                failTest = 1
        return failTest

    @staticmethod
    def failSafe(*args):
        if any(args):
            sys.exit(1)

    #################################################################
    ###Methods calling base functions based on the user given case###
    #################################################################
    def first(self, velo, ite, users):
        self.failSafe(self.createUsers(ite, users))

    def second(self, velo, ite, users):
        self.failSafe(self.authenticateUsers(velo, users))

    def third(self, velo, ite, users):
        self.failSafe(self.createUsers(ite, users), self.authenticateUsers(velo, users))

    def fourth(self, velo, ite, users):
        self.failSafe(self.logoutUsers(velo, users))

    def sixth(self, velo, ite, users):
        self.failSafe(self.authenticateUsers(velo, users), self.logoutUsers(velo, users))

    def seventh(self, velo, ite, users):
        self.failSafe(self.createUsers(ite, users), self.authenticateUsers(velo, users), self.logoutUsers(velo, users))

    def eighth(self, velo, ite, users):
        self.failSafe(self.removeUsers(ite, users))

    def ninth(self, velo, ite, users):
        self.failSafe(self.createUsers(ite, users), self.removeUsers(ite, users))

    def tenth(self, velo, ite, users):
        self.failSafe(self.authenticateUsers(velo, users), self.removeUsers(ite, users))

    def eleventh(self, velo, ite, users):
        self.failSafe(self.createUsers(ite, users), self.authenticateUsers(velo, users), self.removeUsers(ite, users))

    def fourteenth(self, velo, ite, users):
        self.failSafe(self.authenticateUsers(velo, users), self.logoutUsers(velo, users), self.removeUsers(ite, users))

    def fifteenth(self, velo, ite, users):
        self.failSafe(self.createUsers(ite, users), self.authenticateUsers(velo, users), self.logoutUsers(velo, users),
                      self.removeUsers(ite, users))

    @staticmethod
    def default(*args):
        print('The given request is not possible')
        return 1

