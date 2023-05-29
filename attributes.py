import json
import sys
from os import listdir
from os.path import isfile, join

# check if path to terraform files is provided
if(len(sys.argv) < 2):
    print("Please provide the path to the terraform files")
    exit(1)

# read graph.json file
with open('graph.json', 'r') as f:
    data = json.load(f)

# load terraform files
combined_buffer = ""
tffilelist = [f for f in listdir(sys.argv[1]) if isfile(join(sys.argv[1], f) )]
tffilelist = [item for item in tffilelist if ".tf" in item ]
for tffile in tffilelist:
    with open(sys.argv[1] + '/'+ tffile, 'r') as f:
        combined_buffer += f.read()

# remove comments and spaces
tfscript = combined_buffer.replace('\t', '').replace('"','').split("\n")
tfscript = [line.split("#")[0] for line in tfscript]
tfscript = [item for item in tfscript if item != ""]

# Initialize variables
reserved_words = ["resource", "variable", "output", "module", "data", "locals", "provider"]

# Initialize variables
output_list = []
current_prefix = ""

resource_list = []
# Iterate through the lines of the terraform script
for line in tfscript:

    wordlist = line.split()
    if wordlist[0] in reserved_words:
        if wordlist[0] == "variable":
            current_prefix = "var"
            current_suffix = wordlist[1]
            current_name = current_prefix + "." + current_suffix
            resource_list.append(current_name)
        else:
            current_prefix = wordlist[1]
            current_name = current_prefix
            if len(wordlist) > 2 and wordlist[2] != "{":
                current_suffix = wordlist[2]
                current_name = current_prefix + "." + current_suffix
            resource_list.append(current_name)

print(resource_list)

#print(tfscript)