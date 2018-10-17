#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import time
import logging
import argparse
import importlib
from traceback import format_exc

time_start = time.time()

def msg(module,function,message,func, time_start=0, border=40, traceback=None):
    # Logging, according to the time from the beginning of the program.
    time_msg = time.time()
    msg_module = '{}:{}'.format(str(module),str(function))
    if len(msg_module) < border: msg_module += ' ' * (border - len(msg_module))

    msg_time = '{}| Time: {} '.format(msg_module, str(round(time_msg - time_start, 3)))
    if len(msg_time) < (border + 15): msg_time += ' ' * ((border + 15) - len(msg_time))

    msg_out = '{}| -> {}'.format(msg_time, str(message))

    func(msg_out)
    if traceback: func('{}:TRACEBACK: \n\n{}'.format(msg_module, str(traceback)))


def install_lib(name:str,recursion=0,pip='pip3'):
    msg(__name__, 'init:import:{}'.format(name), 'Start.', logging.info,
        time_start=time_start)
    try:
        lib = importlib.import_module(name)
        lib = importlib.reload(lib)
    except:
        msg(__name__, 'init:import:{}'.format(name), 'Not found. Trying install.', logging.warning,
            time_start=time_start)
        try:
            os.system("{} install {}".format(pip,name))
        except:
            msg(__name__, 'init:import:{}'.format(name), 'Failed to install module.', logging.error,
                time_start=time_start, traceback=format_exc())
            sys.exit(1)
        if recursion > 3:
            msg(__name__, 'init:import:{}'.format(name), 'Failed to install module.', logging.error,
                time_start=time_start, traceback=format_exc())
            sys.exit(1)

        recursion += 1
        lib = install_lib(name,recursion=recursion)

    msg(__name__, 'init:import:{}'.format(name), 'Done.', logging.info,
        time_start=time_start)
    return lib

logging.basicConfig(level=logging.INFO)

msg(__name__,'init','Start.', logging.info, time_start=time_start)
msg(__name__,'init:import','Start.', logging.info, time_start=time_start)


try:
    pickle = install_lib('pickle')
    requests = install_lib('requests')
    elastics = install_lib('elasticsearch5')
except:
    msg(__name__, 'init:import', 'Fail.', logging.error, time_start=time_start, traceback=format_exc())
    sys.exit(1)

msg(__name__,'init:import','Done.', logging.info, time_start=time_start)
msg(__name__,'init:load','Start.', logging.info, time_start=time_start)

TEMPLATE_BODY = { "index_patterns": ["logstash-*"],
                  "mappings": {"router":{"properties":{
                                            'connnewdestip': {"type": "ip"},
                                            'connnewsrcip': {"type": "ip"},
                                            'conndestip': {"type": "ip"},
                                            'connsrcip': {"type": "ip"},
                                            'connnewdestport': {"type": "integer"},
                                            'conntime': {"type": "integer"},
                                            'termsent': {"type": "integer"},
                                            'origsent': {"type": "integer"},
                                            'event': {"type": "text","fielddata": True},
                                            'action': {"type": "text","fielddata": True},
                                            'rule': {"type": "text","fielddata": True},
                                            'connrecvif': {"type": "text","fielddata": True},
                                            'conndestif': {"type": "text","fielddata": True}
                 }}}}

class SimpleElasticsearch:
    def __init__(self, host:str, port:int, template:dict):
        msg(__name__, 'elastic_search:init', 'Start.', logging.info, time_start=time_start)
        self.es = None
        self.port = port
        self.hosts = [host]
        self.template = template

        self.connect()
        msg(__name__, 'elastic_search:init', 'Done.', logging.info, time_start=time_start)

    def connect(self):
        try:
            self.es = elastics.Elasticsearch(self.hosts, port=self.port)
        except:
            msg(__name__, 'elastic_search:connect', 'Fail.', logging.error, time_start=time_start, traceback=format_exc())
            sys.exit(1)

    def template_get(self,pattern="*"):
        msg(__name__, 'elastic_search:template_get', 'Search: "{}".'.format(pattern), logging.info,
            time_start=time_start)

        result = self.es.indices.get_template(pattern)
        msg(__name__, 'elastic_search:template_get', 'Found: {}.'.format(str(len(result))), logging.info,
            time_start=time_start)

        return result

    def template_put(self, name):
        msg(__name__, 'elastic_search:template_put', 'PUT: "{}".'.format(name), logging.info,
            time_start=time_start)
        try:
            result = self.es.indices.put_template(name,self.template)
        except:
            msg(__name__, 'elastic_search:template_put', 'Fail: "{}".'.format(name), logging.error,
                time_start=time_start, traceback=format_exc())
            sys.exit(1)

        msg(__name__, 'elastic_search:template_put', 'Done: "{}".'.format(name), logging.info,
            time_start=time_start)
        return result

    def template_exist(self, name:str):
        if name in list(self.template_get()): return True

    def wait(self, recursion=0, max_wait=180):
        msg(__name__, 'elastic_search:wait', 'Wait.', logging.info, time_start=time_start)
        while not self.es.ping():
            recursion += 1
            time.sleep(1)
            if recursion > max_wait:
                msg(__name__, 'elastic_search:wait', 'Fail', logging.error,
                    time_start=time_start, traceback=format_exc())
                sys.exit(1)

        return True

def main(name:str,host:str,port:int,template:dict):
    msg(__name__, 'main:main', 'Start.', logging.info, time_start=time_start)
    obj = SimpleElasticsearch(host,port,template)
    obj.wait()

    answer = obj.template_put(name)
    if not obj.template_exist(name):
        msg(__name__, 'main:main', 'The template was not loaded.', logging.error, time_start=time_start)
        msg(__name__, 'main:main', 'Server response: "{}".'.format(str(answer)), logging.error, time_start=time_start)

    msg(__name__, 'main:main', 'Done.', logging.info, time_start=time_start)
    return True

msg(__name__,'init:load','Done.', logging.info, time_start=time_start)
if __name__ == '__main__':
    msg(__name__, 'main:parser', 'Start.', logging.info, time_start=time_start)
    parser = argparse.ArgumentParser()
    parser.add_argument('name', nargs=1)
    parser.add_argument('--host', default='localhost')
    parser.add_argument('--port', default='9200')
    parser.add_argument('--template')
    args = parser.parse_args()

    msg(__name__, 'main:parser', 'Done.', logging.info, time_start=time_start)
    msg(__name__, 'main:template', 'Start.', logging.info, time_start=time_start)

    try:
        template = TEMPLATE_BODY
        if args.template and os.path.exists(args.template):
            with open(args.template, 'r') as fp:
                template = pickle.load(fp)
    except:
        msg(__name__, 'main:template', 'Fail.', logging.info, time_start=time_start, traceback=format_exc())
        sys.exit(1)

    msg(__name__, 'main:template', 'Done.', logging.info, time_start=time_start)
    if not len(args.name):
        msg(__name__, 'main:args', 'Fail.', logging.info, time_start=time_start)
        sys.exit(1)

    print('\n\n\n')
    main('test', args.host,int(args.port),template)