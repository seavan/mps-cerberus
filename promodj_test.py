#!/usr/bin/env python
# encoding: utf-8

import sys
import os.path
from cerberus import load_config;
from optparse import OptionParser
from cerberus.services.promodj import PromoDJ

config = load_config()

print 'Start test'
pdj_config = config['services']['promodj']
pdj = PromoDJ(pdj_config)
resp = pdj.login()
print resp
