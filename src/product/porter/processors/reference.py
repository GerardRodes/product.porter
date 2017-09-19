# -*- coding: utf-8 -*-

from product.porter.processors.interface import IProcessor


class ReferenceProcessor(IProcessor):

  def extract(self):
    return {
      "value": [item.UID() for item in getattr(self.item, self.field_data['accessor'])()]
    }