# -*- coding: utf-8 -*-

from product.porter.processors.interface import IProcessor
from DateTime import DateTime


def parse_datetime(value):
  if isinstance(value, DateTime):
    return {
      "value":  value.parts(),
      "millis": value.millis(),
    }
    
  else:
    return {
      "value": value
    }


class DatetimeProcessor(IProcessor):
  
  def extract(self):
    value = getattr(self.item, self.field_data['accessor'])()
    return parse_datetime(value)