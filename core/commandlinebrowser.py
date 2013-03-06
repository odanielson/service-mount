
import sys


class CommandLineBrowser(object):

    def __init__(self, model):

        self.model = model
        self.commands = {'create': model.create,
                         'delete': model.delete,
                         'list': model.list,
                         'read': model.read,
                         'update': model.update}
        try:
            self.debugger = (sys.argv[1] == 'debugger')
        except:
            self.debugger = False

    def run(self):
        indata = raw_input('$ ')
        while indata != 'quit':
            if self.debugger:
                import pudb
                pudb.set_trace()
            cmd, delim, args = indata.partition(' ')
            if cmd in self.commands:
                path, delim, rest = args.partition(' ')
                if len(rest) > 0:
                    print self.commands[cmd](path, *rest.split(' '))
                else:
                    print self.commands[cmd](path)
            indata = raw_input('$ ')
