import glob
import argparse
import os
import json

parser = argparse.ArgumentParser(description='build all the command to run classifier tests')
parser.add_argument("-d", "--diroutput", default='/data/chercheurs/brixtel/writeprint/', type=str,
                    help="print result in the dir DIROUTPUT")
parser.add_argument("-t", "--testcorpus", default='', type=str,
                    help="use the TESTCORPUS json file")
parser.add_argument('list_path', metavar='L', type=str, nargs='+',
                    help='List of path L of files containing features, a file per author')

args = parser.parse_args()

##
# args.diroutput
##

if not os.path.isdir(args.diroutput) :
  print 'OUTPUTDIR %s does not exist, create it or choose an other directory'%(args.diroutput)
  exit(0)

##
# args.testcorpus
##

if not os.path.isfile(args.testcorpus) or args.testcorpus == '' :
  print 'TESTCORPUS %s does not exists, create it using build_jeson_corpus_test.py'%(args.testcorpus)
  exit(0)

ftest = open(args.testcorpus, 'r')
json_test = json.load(ftest)
ftest.close()


list_ids_test = [k.encode('utf-8') for k in json_test.keys()]

all_experiments = {
  "xp_mu": (('-d',), [args.diroutput],
            ('-t',), [args.testcorpus],
            ('-i',), list_ids_test)
}

def print_all_experiments(): 
  all_xps = []
  cptout = 0
  for name, arguments in all_experiments.iteritems():
    xps = [["python writeprint.py"]]
    for lst in arguments:
      new_xps = []
      for xp in xps:
        for a in lst:
          new_xps.append(xp + [a])
      xps = new_xps
    all_xps += xps

  for i,xp in enumerate(all_xps):
    print " ".join(xp), '-o %04d.json'%(int(xp[-1])), " ".join(args.list_path)
#    print xp
#    print " ".join(xp), " ".join(args.list_path)
 
print_all_experiments()
