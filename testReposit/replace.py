import argparse
######Arguments parser##############
parser = argparse.ArgumentParser(description=
                                 """Simple description""")

######Argument List###################
parser.add_argument('-param',
                    help="Awesome parameter")
args = parser.parse_args()
print("Displaying parameter " + args.param)