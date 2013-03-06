
__NOTE!__  tool is in early lab status

Service Mount
=============

The purpose of this tool is to be able to mount resources such as databases or WEB API:as to the filesystem.
The primary goal is to create a tool to be used for simple debug purposes which means

1. It should be easy to to add new models for new resources
2. It's not designed or tested for large scale volume usage, but rather for simple inspection of a field here or there.
   With that said, there might be a point in the future where the use in production environments will be considered
   since mounting resources to filesystem could potentially act as a good integration point between different services

The tool consists of a filesystem to model mapper and a base model.
Models for specific resources should override the base model and scripts
should provide tools for mounting resource from the command line.
Take a look at the scripts/zookeeper_mount.py for an example.

Dependencies
------------

* python
* https://github.com/python-zk/kazoo
* http://code.google.com/p/python-llfuse/

Core status
-----------

* Filesystem to model mapper supports basic navigation
  and reading writing to files (not stresstested)
* Filesystem to model mapper lacks ability to create new nodes

Model status
------------

| service | status |
| zookeeper | beta - basic navigation seems to work |

Running
-------

Mount a zookeeper resource with

    # ./scripts/zookeeper_mount.py host mountpath


Adding new models
------------------

TODO


