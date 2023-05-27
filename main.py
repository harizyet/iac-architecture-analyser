import os, re, copy, json

# tf_script_path = "code-under-test"
file_path = os.getcwd()

# print(file_path)
# os.system("cd "+ file_path + "\code-under-test & terraform init")
# os.system("terraform graph | dot -Tdot > graph.dot")

class resourceObj:
    def __init__(self, fullname, name, type, category):
        self.fullname = fullname
        self.name = name
        self.type = type
        self.category = category
        self.dependencies = []
    def __repr__(self):
        return f"<resourceObj name:{self.name} type:{self.type}, category:{self.category}, dependencies:{self.dependencies}>\n"

def extract_res_name(string):
    start_index = string.find("=") + 1
    end_index = string.find(",")
    if start_index < end_index:
        extracted_text = string[start_index:end_index].strip()
        return extracted_text
    else:
        return None

def extract_res_category(string):
    start_index = string.find("=") + 1
    second_index = string.find("=", start_index)
    end_index = string.find("]", second_index)

    if start_index < second_index < end_index:
        extracted_text = string[second_index + 1:end_index].strip()
        return extracted_text
    else:
        return None

def extract_provider(string):            
    start_index = string.find("\\") + 1
    end_index = string.rfind("\\")
    if start_index < end_index:
        extracted_text = string[start_index:end_index].strip()
        return extracted_text
    else:
        return None
    
def extract_parent_tree(string):
    end_index = string.find(">") - 1
    extracted_text = string[0:end_index].strip()
    return extracted_text

def extract_child_tree(string):
    start_index = string.find(">") + 1
    extracted_text = string[start_index:len(string)].strip()
    return extracted_text   

def shape_to_res_category(string):
    match string:
        case "box":
            return "resource"
        case "diamond":
            return "provider"
        case "note":
            return "variable"
        
def extract_name(string):
    start_index = string.find(".") + 1
    extracted_text = string[start_index:len(string)].strip()
    return extracted_text

def get_provider_fullname():
    results = [obj for obj in resourceList if obj.category == "provider"]
    return results[0].fullname

def extract_resource_type(string):
    end_index = string.find(".")
    extracted_text = string[0:end_index].strip()
    return extracted_text

resourceList = []

# load dot file
with open('graph.dot') as rawfile:
    dotlist = rawfile.read()
dotlist = dotlist.replace('\x00', '').replace('\t', '').replace('"','')
dotlist = dotlist.replace('[root] ', '').replace('(expand)','').replace('(close)','')

dotlist = dotlist.split("\n")
dotlist = [item for item in dotlist if item != ""]
dotlist = [item for item in dotlist if "{" not in item and "}" not in item]
dotlist = [item for item in dotlist if "compound" not in item and "newrank" not in item]

# deal with the resources
tempList = []
for row in dotlist:
    if 'shape' in row:
        fullname = extract_res_name(row)
        if 'provider' in fullname:
            fullname = extract_provider(fullname)
        name = extract_name(fullname)
        res_type = extract_resource_type(fullname)
        shape = extract_res_category(row)
        resourceList.append(resourceObj(fullname,name,res_type,shape_to_res_category(shape)))
        
    else:
        newrows = row.replace(' ', '')
        tempList.append(newrows)
dotlist = copy.deepcopy(tempList)

# setup dependencies
tempList.clear()

for branch in dotlist:
    parent = extract_parent_tree(branch)
    if "provider" in parent:
        parent = extract_provider(parent)
    if parent == "root":
        parent = get_provider_fullname()

    child = extract_child_tree(branch)
    if "provider" in child:
        child = extract_provider(child)
    if child == "root":
        child = get_provider_fullname()

    tempList.append([parent,child])

# add dependencies to resourceList
for resource in resourceList:
    for pair in tempList:
        if resource.fullname == pair[0]:
            resource.dependencies.append(pair[1])
        if resource.fullname == pair[1]:
            resource.dependencies.append(pair[0])

# output to json
jsonStr = json.dumps([ob.__dict__ for ob in resourceList])
with open(file_path + '.json', 'w') as f:
    f.write(jsonStr)