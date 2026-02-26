import re, glob, json, datetime
import shutil
from script import convert_byte_to_string

def takeFarmCopy(fileName, takeVersionUp=1):
    currentDir = fileName.split("/farm")[0]
    takeListDir = glob.glob(currentDir+"/*.json")
    takeListDir.sort()
    newFileName = ""

    newNum = "0001"

    if takeListDir:
        currentTake = takeListDir[-1]
        currentCheck = currentTake.split("/")[-1]
        fileNameCheck = fileName.split("/")[-1]

        if currentCheck == fileNameCheck :
            if takeVersionUp == "1" :

                currentNum = re.search("(?<=\.).*[0-9]{4}", currentTake).group()
                newNum = "%04d" % (int(currentNum) + 1)

                newFileName = currentTake.replace("." + currentNum + ".", ".%s." % newNum)

                newFileNameFarm = newFileName.replace("/Take", "/Take/farm")

                shutil.copy2(fileName, newFileNameFarm)

        else :
            newFileName = fileName.replace("/farm", "")
    else:
        newFileName = fileName.replace("/farm", "")

    print(newFileName)
    if takeVersionUp == "1":
        shutil.copy2(fileName, newFileName)


def farmTakeUpdate(fileName):
    currentDir = fileName.split("/farm")[0]
    takeListDir = glob.glob(currentDir+"/take.*.json")
    takeListDir.sort()

    newNum = "0001"

    takeInfoFarm = {}
    with open("%s" % (fileName), 'r') as f:
        takeInfoFarm = json.load(f)

    nowdate = str(datetime.datetime.now())
    date = nowdate.rsplit(":", 1)[0]

    for item in takeInfoFarm:
        for dateDic in takeInfoFarm[item]["date"]:
            takeInfoFarm[item][dateDic] = date

    takeInfo = {}

    if takeListDir:

        currentTake = takeListDir[-1]
        with open("%s" % (currentTake), 'r') as f:
            takeInfo = json.load(f)

        #takeInfo.update(takeInfoFarm)
        newTakeInfo = farmTakeSetInfo(takeInfoFarm, takeInfo)

        currentNum = re.search("(?<=\.).*[0-9]{4}", currentTake).group()
        newNum = "%04d" % (int(currentNum) + 1)

        newFileName = currentTake.replace("." + currentNum + ".", ".%s." % newNum)

        newTakeInfo = convert_byte_to_string.convert_byte_to_string(newTakeInfo)
        with open("%s" % newFileName, 'w') as f:
            #json.dump(takeInfo, f, indent=4)
            json.dump(newTakeInfo, f, indent=4)

        newFileNameJust =newFileName.replace("/take.", "/take_just.")
        takeInfoFarm = convert_byte_to_string.convert_byte_to_string(takeInfoFarm)
        with open("%s" % newFileNameJust, 'w') as fjust:
            #json.dump(takeInfo, f, indent=4)
            json.dump(takeInfoFarm, fjust, indent=4)
    else:
        newFileName = fileName.replace("/farm", "")
        takeInfoFarm = convert_byte_to_string.convert_byte_to_string(takeInfoFarm)
        with open("%s" % newFileName, 'w') as f:
            json.dump(takeInfoFarm, f, indent=4)

        newFileNameJust = newFileName.replace("/take.", "/take_just.")
        takeInfoFarm = convert_byte_to_string.convert_byte_to_string(takeInfoFarm)
        with open("%s" % newFileNameJust, 'w') as fjust:
            #json.dump(takeInfo, f, indent=4)
            json.dump(takeInfoFarm, fjust, indent=4)

    print(("Save json file : {}".format(newFileName)))

def farmTakeSetInfo(farmTake, take):

    for itemType in farmTake:

        if itemType in take:
            keyList = list(take[ itemType ].keys())

            for keyV, itemV in list(farmTake[itemType].items()):
                if keyV in keyList:
                    if type(farmTake[itemType][keyV]) == dict:
                        take[itemType][keyV].update(itemV)
                    else:
                        take[itemType].update({keyV: itemV})
                else:
                    take[itemType].update({keyV: itemV})
        else:
            take[itemType] = farmTake[itemType]

    return take