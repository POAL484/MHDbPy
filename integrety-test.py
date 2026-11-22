import MHDbPy
import responseTypes as respTypes

BLACK = "\u001B[30m"
GREEN = "\u001B[32m"
RED = "\u001B[31m"
YELLOW = "\u001B[33m"
BLUE = "\u001B[34m"
MAGENTA = "\u001B[35m"
CYAN = "\u001B[36m"
RESET = "\u001B[0m"

global partNow, subPartNow
partNow = "unknown"
subPartNow = "unknown"

def startPart(partName: str):
    global partNow
    print(f"{MAGENTA}>>{RESET} Starting part: {YELLOW}{partName}{RESET}")
    partNow = partName

def startSubPart(subPartName: str):
    global partNow, subPartNow
    print(f"{MAGENTA}>>>>{RESET} {YELLOW}{partNow}{RESET} Starting subpart: {CYAN}{subPartName}{RESET}")
    subPartNow = subPartName

def subPartPassed():
    print(f"{GREEN}<<<<{RESET} {YELLOW}{partNow}{RESET} Subpart passed: {GREEN}{subPartNow}{RESET}")

def partPassed():
    print(f"{GREEN}<<{RESET} {YELLOW}{partNow}{RESET} Part {GREEN}passed!{RESET}\n\n")

def assertsValidResp(resp: respTypes.MHDbResponse):
    if not resp.status:
        print(f"{RED}assertValidResp failed:{RESET} Expected {CYAN}valid{RESET} found {YELLOW}http={{{resp.httpCode}}}, errCode={{{resp.code}}}, description={{{resp.description}}}{RESET}")
    assert resp.status
    return resp

print(f"{MAGENTA}> STARTED INTEGRITY TESTS <{RESET}\n\n")

mhdb = MHDbPy.MHDb()

startPart("Set Get Del")

def setGetDelTest(key, value):
    assertsValidResp(mhdb.set(key, value))
    assert assertsValidResp(mhdb.get(key)).value == value
    assert assertsValidResp(mhdb.delete(key)).value == value
    assert assertsValidResp(mhdb.get("str")).value is None

startSubPart("String")
setGetDelTest("str", "tomat")
subPartPassed()

startSubPart("Int")
setGetDelTest("int", 67)
subPartPassed()

startSubPart("Double")
setGetDelTest("double", 6.7)
subPartPassed()

startSubPart("Boolean")
setGetDelTest("bool", True)
setGetDelTest("bool", False)
subPartPassed()

startSubPart("List (straight set get del)")
setGetDelTest("list", [1, 2, 3])
setGetDelTest("list", [])
subPartPassed()

startSubPart("Set (straight set get del)")
setGetDelTest("set", set([1, 67, 48]))
setGetDelTest("set", set())
subPartPassed()

startSubPart("Map (straight set get del)")
setGetDelTest("map", {"67": 67, "48": 48})
setGetDelTest("map", {})
subPartPassed()

partPassed()

def assertByGet(key, value):
    val = assertsValidResp(mhdb.get(key)).value
    if val != value:
        print(f"{RED}assertByGet failed:{RESET} found {YELLOW}{val}{RESET} expected {CYAN}{value}{RESET}")
    assert val == value

startPart("List")

startSubPart("Create and get")
mhdb.createList("list1", 1, 2, 3)
assertByGet("list1", [1, 2, 3])
subPartPassed()

startSubPart("Size")
mhdbList = mhdb.getList("list1")
assert mhdbList.size() == 3
assert assertsValidResp(mhdb.getSize("list1")).size == 3
assert len(mhdbList) == 3
assertsValidResp(mhdb.set("emptyList", []))
assert mhdb.getList("emptyList").size() == 0
assert len(mhdb.createList("list67:1", 67, 67, 67, 67)) == 4
assert len(mhdb.createList("list67:2", 34, 34, 1)) == 3
subPartPassed()

startSubPart("Get item")
assert mhdbList[0] == 1
assert mhdbList[0:2] == [1, 2]
assert mhdbList.getItems([0, 2]) == [1, 3]
assert mhdbList[::-1] == [3, 2, 1]
subPartPassed()

startSubPart("LPush and RPush")
assert mhdbList.addFirst(0) == 4
assert mhdbList.size() == 4
assertByGet("list1", [0, 1, 2, 3])
assert mhdbList.append(67) == 5
assert mhdbList.size() == 5
assertByGet("list1", [0, 1, 2, 3, 67])
subPartPassed()

startSubPart("LPop and RPop")
assert mhdbList.popFirst() == 0
assert mhdbList.size() == 4
assertByGet("list1", [1, 2, 3, 67])
assert mhdbList.pop() == 67
assert mhdbList.size() == 3
assertByGet("list1", [1, 2, 3])
assert mhdbList.pop() == 3 
assert mhdbList.size() == 2                                                 
assertByGet("list1", [1, 2])
subPartPassed()

partPassed()



startPart("Set")

startSubPart("Create and get")
mhdb.createSet("set1", 1, 2, 3)
assertByGet("set1", set([1, 2, 3]))
subPartPassed()

startSubPart("Size")
mhdbSet = mhdb.getSet("set1")
assert mhdbSet.size() == 3
assert assertsValidResp(mhdb.getSize("set1")).size == 3
assert len(mhdbSet) == 3
assertsValidResp(mhdb.set("emptySet", set([])))
assert mhdb.getSet("emptySet").size() == 0
assert len(mhdb.createSet("set67:1", 67, 67, 67, 67, 1, 2)) == 3
assert len(mhdb.createSet("set67:2", 34, 34, 1)) == 2
subPartPassed()

startSubPart("Is member")
assert 1 in mhdbSet
assert not 67 in mhdbSet
assert mhdbSet.contains(3)
assert not mhdb.isMember("set1", 48).isMember
subPartPassed()

startSubPart("SAdd")
assert mhdbSet.add(5) == 4
assert mhdbSet.size() == 4
assertByGet("set1", set([5, 1, 2, 3]))
assert mhdbSet.add(48)
assert mhdbSet.size() == 5
assertByGet("set1", set([1, 2, 3, 48, 5]))
subPartPassed()

startSubPart("SRem")
assert mhdbSet.remove(2) == 2
assert mhdbSet.size() == 4
assertByGet("set1", set([1, 48, 3, 5]))
assert mhdbSet.remove(67) is None
assert mhdbSet.size() == 4
assertByGet("set1", set([1, 1, 1, 48, 3, 5]))
assert mhdbSet.remove(1) == 1
assert mhdbSet.size() == 3                                              
assertByGet("set1", set([3, 48, 5]))
subPartPassed()

partPassed()



startPart("Map")

startSubPart("Create and get")
mhdb.createMap("map1", {"1": 1, "2": 2, "3": 3})
assertByGet("map1", {"1": 1, "2": 2, "3": 3})
subPartPassed()

startSubPart("Size")
mhdbMap = mhdb.getMap("map1")
assert mhdbMap.size() == 3
assert assertsValidResp(mhdb.getSize("map1")).size == 3
assert len(mhdbMap) == 3
assertsValidResp(mhdb.set("emptyMap", dict()))
assert mhdb.getMap("emptyMap").size() == 0
assert len(mhdb.createMap("map67:1", {"q": "q", "w": "w", "r": "r", "t": "t", "y": "y"})) == 5
assert len(mhdb.createMap("map67:2", r=1, t=2, y=7, g=5)) == 4
subPartPassed()

startSubPart("Get item")
assert mhdbMap['1'] == 1
assert mhdbMap['3'] == 3
assert mhdbMap[['1', '2']] == {"1": 1, "2": 2}
assert mhdbMap.getItem("2") == 2
assert mhdbMap.getItem(["1", "3"]) == {"1": 1, "3": 3}
subPartPassed()

startSubPart("Is member")
assert "1" in mhdbMap
assert not "67" in mhdbMap
assert mhdbMap.containsKey("3")
assert not mhdb.isMember("map1", 48).isMember
subPartPassed()

startSubPart("HSet")
mhdbMap['4'] = 4
assert len(mhdbMap) == 4
assertByGet("map1", {"1": 1, "2": 2, "3": 3, "4": 4})
mhdbMap.update({"1": 1, "67": 67})
assert len(mhdbMap) == 5
assertByGet("map1", {"1": 1, "2": 2, "3": 3, "4": 4, "67": 67})
subPartPassed()

startSubPart("HDel")
del mhdbMap['2']
assert len(mhdbMap) == 4
assertByGet("map1", {"1": 1, "3": 3, "4": 4, "67": 67})
assert mhdbMap.delete("67") == 67
assert len(mhdbMap) == 3
assertByGet("map1", {"1": 1, "3": 3, "4": 4})
assert mhdbMap.deleteMany(["1", "3", "5"]) == {"1": 1, "3": 3}
assert len(mhdbMap) == 1
assertByGet("map1", {"4": 4})
del mhdbMap['4']
assert mhdbMap.size() == 0
assertByGet("map1", dict())
subPartPassed()

partPassed()



startPart("Capacity tests")

startSubPart("Add test element")
expectToList = mhdb.createList("should-remove", 1, 2)
assertByGet("should-remove", [1, 2])
subPartPassed()

startSubPart("Dump 200 caches")
for i in range(200):
    assertsValidResp(mhdb.set(f"some{i}", i))
    assertByGet(f"some{i}", i)
subPartPassed()

startSubPart("Test if test element evicted")
assert expectToList.get() is None
subPartPassed()

partPassed()

print(f"\n\n{GREEN}> INTEGRETY TESTS PASSED! (ᵔᴥᵔ) <{RESET}")