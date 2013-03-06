#!/usr/bin/python

import json
import logging
from os.path import sep

from kazoo.client import KazooClient
from kazoo.exceptions import NoNodeError

import sys
sys.path.append('.')
from models.basemodel import BaseModel
from core.commandlinebrowser import CommandLineBrowser

logging.basicConfig(level=logging.DEBUG)


class ZookeeperModel(BaseModel):
    """Zookeeper models maps to a zookeeper instance."""

    def __init__(self, host='localhost'):
        self._childrens = {}
        self._data = ''
        self.host = host

        self.zk = KazooClient(self.host)
        self.zk.start()
        self.special_get = {
            'ZK_DATA': lambda path: self.zk.get(path)[0],
            'ZK_META': lambda path: self._render_meta(
                self.zk.get(path)[1]._asdict())}
        self.special_sizes = {
            'ZK_DATA': lambda path: self.zk.get(path)[1].dataLength,
            'ZK_META': lambda path: len(
                self._render_meta(self.zk.get(path)[1]._asdict()))}
        self.special_set = {
            'ZK_DATA': lambda path, data: self.zk.set(path, data),
            'ZK_META': lambda path, data: None}

    def __del__(self):
        self.zk.stop()

    def _render(self, data):
        """Obsolete. Maybe move it to cmdline browser tool."""
        logging.debug("render(%s)" % (str(data)))
        output = ""
        for row in data:
            output += "%s\n" % (row)
        return output

    def _render_meta(self, meta):
        return "%s\n" % (json.dumps(meta, sort_keys=True,
                                    indent=4, separators=(',', ': ')))

    # NOTE: Working decorator but I see no particular point for using it,
    # just keeping it for reference at the moment
    # def special_files(handler_method):
    #     def handle(self, path):
    #         logging.debug("special_files(%s)" % (str(path)))
    #         main, delim, tail = path.rpartition(sep)
    #         if tail in self.special_get:
    #             if not self.zk.exists(main):
    #                 raise KeyError("%s not found" % (path))
    #             return True
    #         handler_method(self, path)
    #     return handle

    def get_size(self, path):
        logging.debug("get_size(%s)" % (path))
        main, delim, tail = path.rpartition(sep)
        if tail in self.special_sizes:
            return self.special_sizes[tail](main)
        else:
            return 0

    def is_dir(self, path):
        """Return True if node is dir."""
        logging.debug("is_dir(%s)" % (path))
        main, delim, tail = path.rpartition(sep)
        return tail not in self.special_get

    def access(self, path):
        logging.debug("access(%s)" % (path))
        main, delim, tail = path.rpartition(sep)
        if tail in self.special_get:
            if not self.zk.exists(main):
                raise KeyError("%s not found" % (path))
            return True

        if not self.zk.exists(path):
            raise KeyError("%s not found" % (path))
        return True

    def read(self, path, offset=0, count=None):
        offset = int(offset) if offset else 0
        count = int(count) if count else None
        logging.debug("read(%s,%d,%s)" % (path, offset, str(count)))

        main, delim, tail = path.rpartition(sep)
        if tail in self.special_get:
            tmp = self.special_get[tail](main)
        else:
            tmp = self.zk.get(path)[0]
        logging.debug("tmp=%s" % (tmp))
        if count:
            return tmp[offset:(offset+count)]
        else:
            return tmp[offset:]

    def _update(self, path, data):
        main, delim, tail = path.rpartition(sep)
        if tail in self.special_set:
            self.special_set[tail](main, data)
            return len(data)
        else:
            self.zk.set(path, data)
            return len(data)

    def update(self, path, data, offset=None):
        offset = int(offset) if offset else 0
        logging.debug("update(%s,%s,%d)" % (path, str(data), offset))

        if offset is 0:

            return self._update(path, data)

        else:

            tmp = self.read(path)
            tmp = (tmp[0:offset] + data +
                   tmp[offset+len(data):])
            return self._update(path, tmp)

    def create(self, path):
        logging.debug("create(%s)" % (path))
        try:
            self.zk.create(path)
            return True
        except NoNodeError as e:
            logging.debug("Got exception %s" % (str(e)))
            raise KeyError

    def delete(self, path):
        logging.debug("delete(%s)" % (path))
        self.zk.delete(path)

    def list(self, path):
        """List childs at path. Return list with names."""
        logging.debug("list(%s)" % (path))
        children = ['ZK_DATA', 'ZK_META']
        children.extend(self.zk.get_children(path))
        return children

if __name__ == "__main__":

    CommandLineBrowser(ZookeeperModel()).run()
