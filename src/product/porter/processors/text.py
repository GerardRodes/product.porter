# -*- coding: utf-8 -*-

from product.porter.processors.interface import IProcessor


class TextProcessor(IProcessor):
  
  def extract(self):
    return {
      "value": getattr(self.item, self.field_data['accessor'])(),
      "content_type": self.item.getContentType(self.field_name), #This won't work with dexterity
    }