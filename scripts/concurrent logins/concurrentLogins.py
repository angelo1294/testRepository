import requests.packages.urllib3.exceptions
import threading
import argparse
from userHandling import User

requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)


def authenticateUsers(velo='', ite='', users=50, userid='', mode=''):
    for index in range(0, users):
        name = userid + str(index)
        userHandle = User(velo=velo, ite=ite, users=users, username=name, mode=mode)

parser = argparse.ArgumentParser(description=
                                 """NOTE: Script receives number of users to create, login and logout.
                                 Each thread creates number of given users""")

######Argument List###################
parser.add_argument('-users', help='Number of users for each thread to create and authenticate')
parser.add_argument('-threads', help='Number of threads')
parser.add_argument('-ite', help='ITE to create users')
parser.add_argument('-velo', help='Velocity to authenticate users')
parser.add_argument('-createUsers', help='Create users tag')
parser.add_argument('-authenticateUsers', help='Authenticate users tag')
parser.add_argument('-logoutUsers', help='Logout users tag')
parser.add_argument('-deleteUsers', help='Delete users tag')

args = parser.parse_args()

if __name__ == "__main__":
    threads = []
    velo = 'vel-agrama-latest'  # args.velo
    ite = 'ite-agrama-latest'  # args.ite
    users = 4  # args.users
    nrOfThreads = 3  # args.threads
    createUsers = '1'  # args.createUsers
    authenticateUsers = '1'  # args.authenticateUsers
    logoutUsers = '1'  # args.logoutUsers
    deleteUsers = '1'  # args.deleteUsers

    for index in range(0, nrOfThreads):
        userid = 'qatest' + str(index) + 'user'
        mode = createUsers + authenticateUsers + logoutUsers + deleteUsers
        thread = threading.Thread(target=authenticateUsers(velo=velo, ite=ite, users=users, userid=userid, mode=mode))
        threads.append(thread)
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print('Execution complete')
