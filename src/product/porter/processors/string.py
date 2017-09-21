# -*- coding: utf-8 -*-

from product.porter.processors.interface import IProcessor
import unicodedata


class StringProcessor(IProcessor):
  
  def value(self):
    value = self.field_data['value']

    if isinstance(value, unicode):
      value = unicodedata.normalize('NFC', value).encode("utf-8")

    return value