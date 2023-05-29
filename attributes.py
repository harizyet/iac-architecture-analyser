import json
import sys
from os import listdir
from os.path import isfile, join
import hcl2

# check if path to terraform files is provided
if(len(sys.argv) < 2):
    print("Please provide the path to the terraform files")
    exit(1)

# read graph.json file
with open('graph.json', 'r') as f:
    data = json.load(f)

# load terraform files
combined_dict = {}
tffilelist = [f for f in listdir(sys.argv[1]) if isfile(join(sys.argv[1], f) )]
tffilelist = [item for item in tffilelist if ".tf" in item ]
for tffile in tffilelist:
    with open(sys.argv[1] + '/'+ tffile, 'r') as file:
        dict = hcl2.load(file)
    combined_dict = {**combined_dict, **dict}

for x in combined_dict:
    print(x)
    print(combined_dict[x])