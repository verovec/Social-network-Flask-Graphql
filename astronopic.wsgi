#!/usr/bin/python
# -*- coding=utf-8 -*-

import os
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"PATH TO WEB SERVER FOLDER")

from route import app as application
application.secret_key = os.urandom(24)
