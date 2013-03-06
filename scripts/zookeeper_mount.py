#!/usr/bin/python

import sys

import llfuse

sys.path.append('./')
from models.zookeepermodel import ZookeeperModel
from core.modelmount import ModelMount


if __name__ == '__main__':

    if len(sys.argv) < 2:
        raise SystemExit('Usage: %s <mountpoint>' % sys.argv[0])

    mountpoint = sys.argv[1]
    host = sys.argv[2] if len(sys.argv) > 2 else 'localhost'
    operations = ModelMount(ZookeeperModel(host))

    llfuse.init(operations, mountpoint,
                [b'fsname=llfuse_xmp', b"nonempty"])

    # sqlite3 does not support multithreading
    try:
        llfuse.main(single=True)
    except:
        llfuse.close(unmount=False)
        raise

    llfuse.close()
