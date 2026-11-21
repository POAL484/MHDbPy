import requests as req
import uuid
import typing

from responseTypes import *

HEAD = {"user": str(uuid.uuid4())}

class MHDbList:
    
    key: str
    def __init__(self, mhdb, key: str, create: list | None = None):
        self.mhdb = mhdb
        self.key = key
        if create: mhdb.set(key, create)

    def get(self) -> typing.List[typing.Any]:
        return self.mhdb.get(self.key).value

    def __call__(self):
        return self.get()

    def pop(self) -> typing.Any:
        return self.mhdb.pop(self.key).value

    def popFirst(self) -> typing.Any:
        return self.mhdb.popFirst(self.key).value

    def append(self, val: typing.Any):
        self.mhdb.append(self.key, val)

    def insert(self, index: int, val: typing.Any):
        if index == 0: self.mhdb.addFirst(val)
        else:
            l = self()
            if l is None: return
            l.insert(index, val)
            self.mhdb.set(self.key, l)

    def __getitem__(self, s: int | slice):
        if isinstance(s, slice):
            return self.mhdb.getItem(self.key, list(range(*s.indices(self.__len__())))).items
        maybeItem = self.mhdb.getItem(self.key, s).items
        if maybeItem is None: return None
        if len(maybeItem) == 1: return maybeItem[0]
        return maybeItem

    def getItems(self, indexes: typing.List[int]) -> typing.List[typing.Any]:
        return self.mhdb.getItem(self.key, indexes).items

    def __setitem__(self, key: int, value):
        l = self()
        l[key] = value
        self.mhdb.set(self.key, l)

    def __len__(self) -> int:
        size = self.mhdb.getSize(self.key).size
        if size is None: return 0
        return size

    def size(self) -> int:
        return self.__len__()

    def __delitem__(self, key: typing.Literal[0, -1]):
        if key == 0:
            return self.mhdb.popFirst(self.key).value
        elif key == -1:
            return self.mhdb.pop(self.key).value

    def __contains__(self, val):
        l = self()
        if l is None: return False
        return val in l

class MHDbSet:

    key: str
    def __init__(self, mhdb, key: str, create: set | None = None):
        self.mhdb = mhdb
        self.key = key
        if create: mhdb.set(key, {"$set": list(create)})

    def get(self) -> set:
        return self.mhdb.get(self.key).value

    def __call__(self):
        return self.get()

    def contains(self, val: typing.Any) -> bool:
        return self.mhdb.isMember(self.key, val).isMember

    def __contains__(self, item: typing.Any) -> bool:
        return self.contains(item)

    def add(self, val: typing.Any) -> int:
        return self.mhdb.add(self.key, val).size

    def remove(self, val: typing.Any) -> typing.Any:
        return self.mhdb.remove(self.key, val).value

    def __delitem__(self, key):
        self.remove(key)

    def __len__(self) -> int:
        size = self.mhdb.getSize(self.key).size
        if size is None: return 0
        return size

class MHDbMap:

    key: str
    def __init__(self, mhdb, key: str, create: dict | None = None):
        self.mhdb = mhdb
        self.key = key
        if create: mhdb.set(key, create)

    def get(self):
        return self.mhdb.get(self.key).value

    def __call__(self):
        return self.get()

    def __contains__(self, item: typing.Any) -> bool:
        return self.mhdb.isMember(self.key, item).isMember

    def containsKey(self, item: typing.Any) -> bool:
        return self.__contains__(item)

    def __getitem__(self, key):
        items = self.mhdb.getItem(self.key, key).items
        if items is None: return None
        if len(items) == 1: return items[key]
        return items

    def getItem(self, key: str | typing.List[str]) -> typing.Any:
        return self.__getitem__(key)

    def __setitem__(self, key: str, value: typing.Any) -> int:
        return self.mhdb.mapSet(self.key, {key: value}).size

    def __delitem__(self, key) -> typing.Any | None:
        self.mhdb.mapDelete(self.key, key)

    def update(self, dictToUpdate: dict) -> int:
        return self.mhdb.mapSet(self.key, dictToUpdate).size

    def delete(self, key: str) -> dict | None:
        deleted = self.mhdb.mapDelete(self.key, key).deleted
        return deleted[list(deleted.keys())[0]] if deleted else None

    def deleteMany(self, keys: list) -> dict | None:
        return self.mhdb.mapDelete(self.key, keys).deleted

    def __len__(self) -> int:
        size = self.mhdb.getSize(self.key).size
        if size is None: return 0
        return size

class MHDb:
    host: str

    def __init__(self, host = "http://localhost:5445/"):
        self.host = host

    def makeOperation(self, op: str, **kwargs):
        return req.post(self.host, headers=HEAD, json={"op": op, **kwargs}).json()

    def set(self, key: str, value: typing.Any) -> MHDbSetResponse:
        if value is set:
            value = {"$set": value}
        return MHDbSetResponse(
            value,
            self.makeOperation("SET", key = key, value = value)
        )

    def get(self, key: str) -> MHDbValueResponse:
        return MHDbValueResponse(self.makeOperation("GET", key = key))

    def getItem(self, key: str, items: int | str | typing.List[str | int]) -> MHDbValueResponse:
        if ( not isinstance(items, list) ): items = [items]
        return MHDbValueResponse(self.makeOperation("GETITEM", key = key, item = items))

    def isMember(self, key: str, value: typing.Any) -> MHDbIsMemberResponse:
        return MHDbIsMemberResponse(self.makeOperation("ISMEMBER", key = key, value = value))

    def getSize(self, key: str) -> MHDbSizeResponse:
        return MHDbSizeResponse(self.makeOperation("SIZE", key = key))

    def inc(self, key: str, n: int | float) -> MHDbIncDecResponse:
        return MHDbIncDecResponse(self.makeOperation("INC", key = key, value = n))

    def dec(self, key: str, n: int | float) -> MHDbIncDecResponse:
        return MHDbIncDecResponse(self.makeOperation("DEC", key = key, value = n))

    def add(self, key: str, value: typing.Any) -> MHDbSizeResponse:
        obj = self.get(key).value
        if isinstance(obj, list):
            return self.append(key, value)
        return MHDbSizeResponse(self.makeOperation("SADD", key = key, value = value))

    def append(self, key: str, value: typing.Any) -> MHDbSizeResponse:
        return MHDbSizeResponse(self.makeOperation("RPUSH", key = key, value = value))

    def addFirst(self, key: str, value: typing.Any) -> MHDbSizeResponse:
        return MHDbSizeResponse(self.makeOperation("LPUSH", key = key, value = value))

    def pop(self, key: str) -> MHDbValueResponse:
        return MHDbValueResponse(self.makeOperation("RPOP", key = key))

    def popFirst(self, key: str) -> MHDbValueResponse:
        return MHDbValueResponse(self.makeOperation("LPOP", key = key))

    def remove(self, key: str, value: typing.Any) -> MHDbValueResponse:
        return MHDbValueResponse(self.makeOperation("SREM", key = key, value = value))

    def delete(self, key: str) -> MHDbValueResponse:
        return MHDbValueResponse(self.makeOperation("DEL", key = key))

    def mapSet(self, key: str, update: dict) -> MHDbSizeResponse:
        return MHDbSizeResponse(self.makeOperation("HSET", key = key, value = update))

    def mapDelete(self, key: str, mapKey: str | typing.List[str]) -> MHDbMapDeletedResponse:
        if not isinstance(mapKey, list):
            mapKey = [mapKey]
        return MHDbMapDeletedResponse(self.makeOperation("HDEL", key = key, mapKeys = mapKey))

    def createList(self, key: str, *args) -> MHDbList:
        return MHDbList(self, key, args)

    def getList(self, key: str) -> MHDbList | None:
        obj = self.get(key).value
        return MHDbList(self, key) if isinstance(obj, list) else None

    def createSet(self, key: str, *args) -> MHDbSet:
        return MHDbSet(self, key, args)

    def getSet(self, key: str) -> MHDbSet | None:
        obj = self.get(key).value
        return MHDbSet(self, key) if isinstance(obj, set) else None

    def createMap(self, key: str, dictArgs = {}, **kwargs) -> MHDbMap:
        dictArgs.update(kwargs)
        return MHDbMap(self, key, dictArgs)

    def getMap(self, key: str) -> MHDbMap | None:
        obj = self.get(key).value
        return MHDbMap(self, key) if isinstance(obj, dict) else None
