import argparse
from restRequests import getUsers, putUser

######Arguments parser##############
parser = argparse.ArgumentParser(description=
                                 """NOTE: Script receives number of users to create, login and logout.
                                 Each thread creates number of given users""")

######Argument List###################
parser.add_argument('-velo', help='Velocity to authenticate users')

args = parser.parse_args()

if __name__ == "__main__":
    velo = 'vel-calix-test1'  # args.velo
    putUser(velo, getUsers(velo), 'noreply@mail.com')
