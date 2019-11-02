from enum import Enum
from functools import total_ordering


@total_ordering
class OrderedEnum(Enum):
    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented

    def succ(self):

        found = False

        for v in self.__class__:
            if v == self:
                found = True
            if found:
                return v
        return None
