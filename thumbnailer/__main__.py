import logging
import os
import sys
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

import thumbnailer

t = thumbnailer.Thumbnailer(Polling=True)
