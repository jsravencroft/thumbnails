import boto3
from   datetime import datetime
import json
import os
from   PIL import Image
import pytest

from thumbnailer import Thumbnailer

_module_path =  os.path.dirname(__file__)

class TestThumbnailer:

  def test_image_good(self):
    write_image = Image.open(os.path.join(os.path.dirname(__file__), 'rainier.jpg'))
    t = Thumbnailer()
    thumb_image = t.make_thumbnail(write_image)

    assert thumb_image.size == (100, 100)
    write_image.show()
    thumb_image.show()

  def test_image_bad(self):
    t = Thumbnailer()
    with pytest.raises(Exception):
      thumb = t.make_thumbnail("Not an image")
