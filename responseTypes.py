import typing

class MHDbResponse:
    status: bool
    description: str
    code: int
    httpCode: int
    data: dict
    def __init__(self, parsedJson: dict):
        self.status = parsedJson['status'] == 200
        self.httpCode = parsedJson['status']
        self.description = parsedJson['err'] if 'err' in parsedJson else None
        self.code = parsedJson['errCode'] if 'errCode' in parsedJson else None
        self.data = parsedJson['data'] if 'data' in parsedJson else None

    def parseObject(self, value: typing.Any) -> typing.Any:
        if isinstance(value, dict):
            if '$set' in value:
                if isinstance(value['$set'], list):
                    return set(value['$set'])
        return value

class MHDbSetResponse(MHDbResponse):
    inserted: typing.Any
    def __init__(self, inserted: typing.Any, parsedJson: dict):
        super().__init__(parsedJson)
        self.inserted = inserted if self.status else None

class MHDbValueResponse(MHDbResponse):
    value: typing.Any
    def __init__(self, parsedJson: dict):
        super().__init__(parsedJson)
        self.value = self.parseObject(self.data['value']) if self.data and 'value' in self.data else None
        
class MHDbIsMemberResponse(MHDbResponse):
    isMember: bool
    def __init__(self, parsedJson):
        super().__init__(parsedJson)
        self.isMember = self.data['isMember'] if self.data and self.status else False

class MHDbSizeResponse(MHDbResponse):
    size: int
    def __init__(self, parsedJson):
        super().__init__(parsedJson)
        self.size = self.data['size'] if self.data and self.status else None

class MHDbIncDecResponse(MHDbResponse):
    value: int | float
    def __init__(self, parsedJson):
        super().__init__(parsedJson)
        self.value = self.data['value'] if self.data and self.status else None

class MHDbMapDeletedResponse(MHDbResponse):
    deleted: dict
    def __init__(self, parsedJson):
        super().__init__(parsedJson)
        self.deleted = self.data['deleted'] if self.data and self.status else None