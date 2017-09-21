# -*- coding: utf-8 -*-

from product.porter.processors.interface import IProcessor
import unicodedata


class TextProcessor(IProcessor):
  
  def extract(self):
    return {
      "value": self.accessor(),
      "content_type": self.item.getContentType(self.field_name), #This won't work with dexterity
    }

    
  def value(self):
    value = self.field_data['value']

    if isinstance(value, unicode):
      value = unicodedata.normalize('NFC', value).encode("utf-8")

    return value