#!/usr/bin/python
from __future__ import division, print_function, absolute_import

from os import getuid, getgid
from os.path import sep
from threading import Lock
import errno
import logging
import stat
import time

import llfuse

logging.basicConfig(level=logging.DEBUG)


class InodeLibrary(object):

    inode_index = long(1)

    def __init__(self):
        self.inodes = {}
        self.pathes = {}
        self.lookup_inode('/')

    def _create(self, path):
        """Create inode for path. Not threadsafe,
        must be called from locked context.
        """
        inode = self.inode_index
        self.inode_index += 1

        self.inodes[inode] = path
        self.pathes[path] = inode
        return inode

    def lookup_path(self, inode):
        """Return path."""
        logging.debug("lookup_path(%s) %s" % (str(inode),
                                              (inode in self.inodes)))
        return self.inodes[inode]

    def lookup_inode(self, path):
        """Return inode."""
        logging.debug("lookup_inode(%s)" % (path))
        while path.find(sep+sep) >= 0:
            path = path.replace(sep+sep, sep)
        logging.debug("cleaned inode to (%s)" % (path))

        with Lock():
            if path in self.pathes:
                return self.pathes[path]
            else:

                inode = self._create(path)
        return inode


class ModelMount(llfuse.Operations):

    def __init__(self, model):
        super(llfuse.Operations, self).__init__()
        self.model = model
        self.inodes = InodeLibrary()
        self.uid = getuid()
        self.gid = getgid()

    # def statfs(self):
    #     logging.debug("statfs()")

    # def readlink(self, inode):
    #     logging.debug("readlink(%s)" % (inode))

    # def unlink(self, inode_p, name):
    #     logging.debug("unlink(%s,%s)" % (inode_p, name))

    # def rmdir(self, inode_p, name):
    #     logging.debug("rmdir(%s,%s)" % (inode_p, name))

    # def symlink(self, inode_p, name, target, ctx):
    #     logging.debug("symlink(%s,%s,%s,%s)" % (inode_p, name, target, ctx))

    # def rename(self, inode_p_old, name_old, inode_p_new, name_new):
    #     logging.debug("rename(%s,%s,%s,%s)" % (inode_p_old, name_old,
    #                                            inode_p_new, name_new))

    # def link(self, inode, new_inode_p, new_name):
    #     logging.debug("link(%s,%s,%s)" % (inode, new_inode_p, new_name))

    # def mknod(self, inode_p, name, mode, rdev, ctx):
    #     logging.debug("mknod(%s,%s,%s,%s,%s)" % (inode_p, name, mode,
    #                                              rdev, ctx))

    # def mkdir(self, inode_p, name, mode, ctx):
    #     logging.debug("mkdir(%s,%s,%s,%s)" % (inode_p, name, mode, ctx))

    # def create(self, inode_parent, name, mode, flags, ctx):
    #     logging.debug("create(%s,%s,%s,%s,%s)" % (inode_parent, name, mode,
    #                                               flags, ctx))

    #############################
    # Functions above not ready #
    #############################

    def _createattr(self, inode):
        logging.debug("createattr(%s)" % (str(inode)))
        path = self.inodes.lookup_path(inode)
        current_time = int(time.time())

        entry = llfuse.EntryAttributes()
        entry.st_ino = inode
        entry.generation = 0
        entry.entry_timeout = 300
        entry.attr_timeout = 300
        entry.st_mode = (stat.S_IRUSR | stat.S_IWUSR |
                         stat.S_IXUSR | stat.S_IRGRP | stat.S_IXGRP |
                         stat.S_IROTH | stat.S_IXOTH)
        if self.model.is_dir(path):
            entry.st_mode |= stat.S_IFDIR
        else:
            entry.st_mode |= stat.S_IFREG

        entry.st_nlink = 0  # Links not supported?

        entry.st_uid = self.uid
        entry.st_gid = self.gid
        entry.st_rdev = 0  # What is this?
        entry.st_size = self.model.get_size(path)

        entry.st_blksize = 512
        entry.st_blocks = 1

        entry.st_atime = current_time
        entry.st_mtime = current_time
        entry.st_ctime = current_time

        return entry

    def getattr(self, inode):
        logging.debug("getattr(%s)" % (inode))
        return self._createattr(inode)

    def setattr(self, inode, attr):
        logging.debug("setattr(%s,%s)" % (inode, attr))
        return self.getattr(inode)

    def open(self, inode, flags):
        logging.debug("open(%d,%s)" % (inode, str(flags)))
        return inode

    def release(self, fh):
        logging.debug("release(%s)" % (fh))

    def read(self, fh, offset, length):
        logging.debug("read(%d,%d,%d)" % (fh, offset, length))
        return self.model.read(self.inodes.lookup_path(fh), offset, length)

    def write(self, fh, offset, buf):
        logging.debug("write(%s,%s,%s)" % (fh, offset, buf))
        return self.model.update(self.inodes.lookup_path(fh), buf, offset)

    def access(self, inode, mode, ctx):
        """Implemens access check. Always return True."""
        logging.debug("access called for %s %s %s" % (inode, mode, ctx))
        # Yeah, could be a function and has unused arguments
        #pylint: disable=R0201,W0613
        return True

    def opendir(self, inode):
        logging.debug("opendir called for inode %s" % (inode))
        return inode

    def readdir(self, inode, off):
        logging.debug("readdir called for %s %s" % (inode, off))

        path = self.inodes.lookup_path(inode)
        childs = self.model.list(path)
        for node in childs[off:]:
            off += 1
            full_path = '%s/%s' % (path, node)
            logging.debug("yielding %s" % (full_path))
            yield (node,
                   self._createattr(self.inodes.lookup_inode(full_path)),
                   off)

    def lookup(self, inode_p, name):
        logging.debug("lookup(%s,%s)" % (inode_p, name))

        if name == '.':
            inode = inode_p
        elif name == '..':
            logging.debug("WARNING!!!!")
            assert False, "lookup of .. not implmented"
        else:
            try:
                base_path = self.inodes.lookup_path(inode_p).strip(sep)
                full_path = sep.join([base_path.strip(sep), name])
                self.model.access(full_path)
                inode = self.inodes.lookup_inode(full_path)
            except KeyError:
                logging.debug("path not found")
                raise(llfuse.FUSEError(errno.ENOENT))

        return self._createattr(inode)
