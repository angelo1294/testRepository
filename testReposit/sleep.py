import argparse, time, os
######Arguments parser##############
parser = argparse.ArgumentParser(description=
                                 """Simple description""")

######Argument List###################
parser.add_argument('-time', help="Time to sleep")
parser.add_argument('-env', help="Show environment variables")
parser.add_argument('-params', help="Print all received parameters")
args = parser.parse_args()


if args.time: 
	time.sleep(int(args.time))
if args.env:
	print('Environment variables: \n' + os.environ['HOME'] + '\n')
if args.params:
	print("Received parameters: " + str(args))