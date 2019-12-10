import logging
import os
import sys
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

import api
port = 5000

if 'PORT' in os.environ:
  try:
    port = os.getenv('PORT')
  except:
    pass
api.serve(api.app, host="0.0.0.0", port=port)
