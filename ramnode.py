#!/usr/bin/python

import logging
from os.path import sep

from basemodel import BaseModel
from commandlinebrowser import CommandLineBrowser

logging.basicConfig(level=logging.DEBUG)

class RamNode(BaseModel):
    """Rammode stores a ramdisk in ram nodes."""

    def __init__(self):
        self._childrens = {}
        self._data = ''

    def _render(self, data):
        logging.debug("render(%s)" % (str(data)))
        output = ""
        for row in data.keys():
            output += "%s\n" % (row)
        return output

    def read(self, path, offset = 0, count = None):
        offset = int(offset) if offset else 0
        count = int(count) if count else None
        logging.debug("read(%s,%d,%s)" % (path, offset, str(count)))
        node, delim, rest = path.partition(sep)
        if rest is '' or rest is sep:
            if count:
                return self._data[offset:(offset+count)]
            else:
                return self._data[offset:]
        else:
            return self._childrens[node].read(rest, offset, count)

    def update(self, path, data, offset = None):
        offset = int(offset) if offset else 0
        logging.debug("update(%s,%s,%d)" % (path, str(data), offset))
        node, delim, rest = path.partition(sep)
        if rest is '' or rest is sep:
            self._data = (self._data[0:offset] + data +
                          self._data[offset+len(data):])
        else:
            return self._childrens[node].update(rest, data, offset)

    def create(self, path):
        logging.debug("create(%s)" % (path))
        node, delim, rest = path.partition(sep)
        if rest is '' or rest is sep:
            self._childrens[node] = RamNode()
            return True
        else:
            return self._childrens[node].create(rest)

    def delete(self, path):
        logging.debug("delete(%s)" % (path))
        node, delim, rest = path.partition(sep)
        if rest is '' or rest is sep:
            del self._childrens[node]
        else:
            return self._childrens[node].delete(rest)

    def list(self, path):
        logging.debug("list(%s)" % (path))
        node, delim, rest = path.partition(sep)
        if node is '' or node is sep:
            return self._render(self._childrens)
        else:
            return self._childrens[node].list(rest)


if __name__=="__main__":

    CommandLineBrowser(RamNode()).run()
