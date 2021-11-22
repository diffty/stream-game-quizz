from utils import to_json


class Serializable:
    def to_json(self):
        return to_json(self.__dict__)

    def from_json(self, data):
        for k, v in data.items():
            if k in self.__dict__:
                item = self.__dict__[k]
                if isinstance(item, Serializable):
                    item.from_json(v)
                    continue
                elif type(item) == bool:
                    self.__dict__[k] = v == "true"
                else:
                    self.__dict__[k] = type(item)(v)