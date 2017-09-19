# -*- coding: utf-8 -*-

from product.porter.processors.file import FileProcessor
from OFS.Image import Image as OFSImage
from OFS.Image import Pdata



class ImageProcessor(FileProcessor):
  
  def get_data(self):
    file = self.item.getField('image')
    img  = file.getScale(self.item)
    data = None

    if isinstance(img, OFSImage):
      data = str(img.data)
    elif isinstance(img, Pdata):
      data = str(img)
    elif isinstance(img, str):
      data = img
    elif isinstance(img, file) or (hasattr(img, 'read') and hasattr(img, 'seek')):
      img.seek(0)
      return img

    if data:
      return data
    else:
      return None