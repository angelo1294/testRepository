import sys, json
from restRequests import iteUserHandling, getToken, userLogout, getUsers, putUser, getUser

class User:
    def __init__(self, username='qatestuser'):
        self.username = username
    #####################################################################
    ###Base functions for create users, login, logout and remove users###
    #####################################################################

    def userHandling(self, velo, ite, users, mode='1111'):
        switcher = {
            '0000':      "self.default",
            '1000':      "self.failSafe(self.createUsers(ite, users))",
            '0100':      "self.failSafe(self.authenticateUsers(velo, users))",
            '1100':      "self.failSafe(self.createUsers(ite, users), self.authenticateUsers(velo, users))",
            '0010':      "self.failSafe(self.logoutUsers(velo, users))",
            '1010':      "self.default",
            '0110':      "self.failSafe(self.authenticateUsers(velo, users), self.logoutUsers(velo, users))",
            '1110':      "self.failSafe(self.createUsers(ite, users), self.authenticateUsers(velo, users), self.logoutUsers(velo, users))",
            '0001':      "self.failSafe(self.removeUsers(ite, users))",
            '1001':      "self.failSafe(self.createUsers(ite, users), self.removeUsers(ite, users))",
            '0101':      "self.failSafe(self.authenticateUsers(velo, users), self.removeUsers(ite, users))",
            '1101':      "self.failSafe(self.createUsers(ite, users), self.authenticateUsers(velo, users), self.removeUsers(ite, users))",
            '0011':      "self.default",
            '1011':      "self.default",
            '0111':      "self.failSafe(self.authenticateUsers(velo, users), self.logoutUsers(velo, users), self.removeUsers(ite, users))",
            '1111':      "self.failSafe(self.createUsers(ite, users), self.authenticateUsers(velo, users), self.logoutUsers(velo, users), self.removeUsers(ite, users))"
        }
        if len(mode) > 4:
            print('Bad parameters were given for execution')
            sys.exit(1)
        elif len(mode) < 4:
            mode = mode + '0' * (4 - len(mode))
        exec(switcher[mode])

    def userMessaging(self, success=[], fail=[]):
        if not fail:
            print("All users updated successfully : " +  '\n' + str(success))
        else:
            print("Successfully updated users: " + '\n' + str(success) + '\n' + "Failed to update users:\n" + str(fail))

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
            print('remove'+name)
            result = iteUserHandling(ite=ite, mode='delete', userid=name, name=name, password=name)
            if not result:
                print('User ' + name + ' has not been deleted')
                failTest = 1
        return failTest

    def loginUserList(self, velo, userCredentials):
        """
        Function receives dictionary:
            user1: [password1]
        Authenticates the user and returns:
            user1: [password1, token1]
        """
        for user in userCredentials:
            userCredentials[user].append(getToken(velo, user, userCredentials[user][0]))
        return userCredentials

    def changeUserRole(self, velo='', userList=[], role='ADMIN'):
        """
        Receives an user list to update specific users roles
        """
        success = []
        fail = []
        if role == 'ADMIN':
            filterRole ='USER'
        else:
            filterRole = 'ADMIN'
        response = getUsers(velo=velo, role=filterRole)
        if userList:
            for user in userList:
                rq = putUser(velo=velo, userId=getUser(velo=velo, loginName=user), body={'role': role})
                if rq['role'] != role or 'errorId' in rq:
                    fail.append(user)
                else:
                    success.append(user)
        else:
            for user in response:
                rq = putUser(velo=velo, userId=response[user]['id'], body={'role': role})
                if rq['role'] != role or 'errorId' in rq:
                    fail.append(user)
                else:
                    success.append(user)
        self.userMessaging(success=success, fail=fail)

    def changeEmail(self, velo='', email=''):
        success = []
        fail = []
        users = getUsers(velo=velo)
        for user in users:
            rq = putUser(velo=velo, userId=users[user]['id'], body={'email': email})
            if 'errorId' in rq:
                fail.append(user)
            else:
                success.append(user)
        self.userMessaging(success=success, fail=fail)


    @staticmethod
    def failSafe(*args):
        if any(args):
            sys.exit(1)


    @staticmethod
    def default(*args):
        print('The given request is not possible')
        return 1