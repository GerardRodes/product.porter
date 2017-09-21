# -*- coding: utf-8 -*-

from product.porter.processors.interface import IProcessor
from DateTime import DateTime


def parse_datetime(value):
  # To json
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
    return parse_datetime(self.accessor())


  def value(self):
    value = self.field_data['value']
    if value:
      value = DateTime(value[0], value[1], value[2], value[3], value[4], value[5], value[6])
      return value
    else:
      return None