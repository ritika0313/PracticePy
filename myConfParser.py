import sys
from time import perf_counter
import functools


'''
1. Build a nested dictionary with "group" as first level key and "setting" as level 2 key. 
    It will store the values as mentioned in the config file which can be a string, number, list or a boolean value
    - Read the contents of the file and parse them to find the find "group", "setting" and "value" to build the dictionary
    - Proper handling of various invalid/valid formats of configuration in config file. 
    - Exiting from function in case of error.

2. Convert index based dictionary to dotted format using in-built dotted_dict module. 
    Override the getter function to avoid the error raised for missing leaf values. 
    Return the dictionary

'''
# LT = represents index 0 for Left part of the pair
# RT = represents index 1 for Right part of the pair
# setOver_value[LT] = setting<override> , setOver_value[RT] = value
# setting_override[LT] = setting , setting_override[RT] = override
LT = 0
RT = 1

class DotDict(dict):
    def __getattr__(self, name):
        return self.get(name, None)               
    
# Function to return a list, in case input parameter has multiple values
# Otherwise if single element input -check if its a string for a boolean value and return True/False accordingly
#                                   -If not, return back the received value
def assign_value(valueList):
    if len(valueList) > 1:
        return valueList
    elif valueList[0] in ('no', '0', 'false'):
        return False
    elif valueList[0] in ('yes', '1', 'true'):
        return True
    else:
        return valueList[0]        
        
def parse_value(valueStr):
    if ';' in valueStr:
        # strip off any trailing comments after config
        valueList = valueStr.split(';')
        valueList = valueList[LT].strip()                    
    else:
        valueList = valueStr.strip()

    # If valueList is not a string, check for a list presence
    if valueList[0] != '\"':
        valueList = valueList.split(',')

    valueList = assign_value(valueList)
    return valueList

# Returns -1 as error condition    
def parse_override_and_check_dict_update(override):
    overrideLen = len(override)
    if override[overrideLen - 1] != '>':
        print(f'ERROR: Invalid format for override')
        return -1
    overrideVal = override[:overrideLen-1].strip()
    
    # If override is enabled, update the dict using current config line value
    # Otherwise no update is needed
    if overrideVal in overrides:
        return True
    else:
        return False  

# Returns setting = -1 as error condition
def parse_setting_overrideValue(configLine):
    updateDict = False
    # Extract setting-value pair from config lines with format: setting<override> = value
    setOver_value = configLine.split('=')            
    
    # if more than 1 or no demiliter('=') is present OR
    # no value is specified for the setting after '=' in config lines
    if len(setOver_value) != 2 or setOver_value[RT] == "":
        print(f'ERROR: Incorrect format for the setting : {setOver_value[LT]}, no of elements: {len(setOver_value)}')
        return -1, 0, 0
    else:
        #print(f'DEBUG: setting : {setOver_value[LT]} , value: {setOver_value[RT]}')
        # Extract setting-override pair
        setting_override = setOver_value[LT].split('<')
        
        # Extract setting from left part
        setting = setting_override[LT].strip()
        if setting == "" or setting[LT][0] == '>':
            print("ERROR: incorrect format for setting")            
            return -1, 0, 0            
        
        # Extract value from right part 
        valueList = parse_value(setOver_value[RT])  

        #if override is specified
        if len(setting_override) == 2:
            updateDict = parse_override_and_check_dict_update(setting_override[RT].strip())

        # If no override is specified, just assign the default value mentioned in the current config line
        else:
            updateDict = True
        return setting, valueList, updateDict

def load_config(file_path, overrides=[]) :
    try:
        with open(file_path, 'r') as configFile:
            content = configFile.read()
            lines = content.split('\n')
    except FileNotFoundError:
        print("ERROR: File not found!")
        return
    except :
        print("ERROR: A file error occured")
        return

    configDict = {}
    
    for configLine in lines:           
        configLine = configLine.strip()
        #print(f'DEBUG: config line : {configLine}') 

        line_len = len(configLine)
        if line_len == 0 or configLine[0] == ';':            
            continue

        if configLine[0] == '[':
            if configLine[line_len-1] != ']':
                print("ERROR: Invalid format for group")
                return
            group = (configLine[1:-1])
                
            if " " in group:
                print(f'ERROR: Invalid group name: {group}')
                return
            # If a group already exists, new group shall not be created 
            # and just the following config lines shall be parsed to append its settings
            if group not in configDict:
                configDict[group] = {}
        else:
            if not configDict:
                print("ERROR: First config group missing")
                return
            setting, value, updateDict = parse_setting_overrideValue(configLine)
            if setting == -1 or updateDict == -1:
                return
            if updateDict == True:                
                configDict[group][setting] = value

    # Convert to dotted notation dictionary
    configDict = DotDict(configDict)
    for group in configDict:
        configDict[group] = DotDict(configDict[group])
    
    return configDict


def test_samples(CONFIG):
    print("----------Validating test samples-----------")
    assert CONFIG.common.paid_users_size_limit == '2147483648'
    assert CONFIG.ftp.name == "\"hello there, ftp uploading\""
    assert CONFIG.http.params == ["array", "of", "values"]
    assert CONFIG.ftp.lastname == None
    assert CONFIG.ftp.enabled == False
    #assert CONFIG.ftp['path'] == '/etc/var/uploads'

    # For testing symbol '*' in overrides
    assert CONFIG.ftp['path'] == '/srv/newtest'
    
    #print(CONFIG.common)
    #print(CONFIG.ftp)
    #print(CONFIG.http)
    
    print("--------------------SUCCESSFUL----------------")    


'''
# Use built-in LRU cache for optimizing split function
@functools.lru_cache
def query_split(q):
    return tuple(q.split('.'))

def query_dict(cDict, queryPath):    
    pathTuple = query_split(queryPath)
    
    for key in pathTuple:        
        cDict = cDict[key]    
    return cDict     

'''

# Create a cache to store the frequent queries
# cache key = dotted notation path , value = result value/dict
# eg. cache[ftp.enabled] = no

cache = {} 
def query_dict(cDict, queryPath):
    global cache
    
    try:        
        # If query is present in the cache
        cDict = cache[queryPath]
        
    except KeyError:
        # If query is encountered first time        
        pathTuple = tuple(queryPath.split('.'))
               
        # Find value by accessing each element in the tuple
        
        for key in pathTuple:        
            cDict = cDict[key]
        cache[queryPath] = cDict
    return cDict

if __name__ == "__main__":
    #global CONFIG
    arg_count = len(sys.argv)
    # Can specify overrides as command line arguments
    if arg_count > 1 :
        overrides = []
        for i in range(1, arg_count):
            overrides.append(sys.argv[i])
    else:
        # Default overrides
        overrides = ["ubuntu", "production", '*']

    #t1_start = perf_counter()   
    #for i in range(0,1) :
        CONFIG = load_config('srvSettings.conf', overrides)
    #t1_stop = perf_counter()
    #print("DEBUG: Elapsed time for load_config processing (s):",t1_stop-t1_start)

    if CONFIG == None:
        print("Exiting")
        exit()

    # Validate few sample queries
    test_samples(CONFIG)

    t2_start = perf_counter() 
    for i in range(0,5000):
        result = query_dict(CONFIG, 'ftp.name')           
    t2_stop = perf_counter() 
    print("DEBUG: Elapsed time for query processing (s):",t2_stop-t2_start)
    #print(f'DEBUG: result = {result}')
