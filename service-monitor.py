#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from time import sleep, time
import sys

service_configs = {
    ## sevicename: timeout
    'hmi-mainfu'            : 5,
    'hmi-phonefu'           : 5,
    'hmi-displaysettingsfu' : 5,
}

class Service:
    def __init__(self, servicename, timeout):
        self.servicename=servicename
        self.timeout=timeout
        self.activating_time = None
        self.coredumped = False
    
    def check(self):
        state = os.popen('systemctl is-active '+self.servicename).read().rstrip()
        if not self.activating_time and state == 'activating':
            print('Activating service {}'.format(self.servicename))
            self.activating_time = time()
        elif self.activating_time and state == 'active':
            print('Service {} is active'.format(self.servicename))
            self.activating_time = None
        if state == 'activating' and time() - self.activating_time > self.timeout and not self.coredumped:
            self.coredumped = True
            self.dump()

    def pid(self):
        return os.popen('systemctl --no-pager show --property MainPID --value {}'.format(self.servicename)).read().rstrip()        
    
    def dump(self):
        print('Initiating {} coredump'.format(self.servicename))
        os.system('touch /apps_data/dlt-core/{}.{}.gz.timeout'.format(self.servicename, self.pid()))
        os.system('systemctl kill -s SIGSEGV --kill-who=main {}'.format(self.servicename))


services = [Service(s, t) for s, t in service_configs.items()]

while True:
    for s in services:
        s.check()
    sys.stdout.flush()
    sleep(.5)
        
