# -*- coding: utf-8 -*-

from product.porter.processors.interface import IProcessor


class BooleanProcessor(IProcessor):

  def extract(self):
    value = self.accessor()

    if isinstance(value, str):
      if value.lower() in ("false", "no"):
        value = False
    elif value:
      value = True
    else:
      value = False

    return {
      "value": value
    }


  def value(self):
    """
      Sets the field value to the item
    """

    value = self.field_data['value']

    if isinstance(value, str):
      if value.lower() in ("true", "si"):
        value = True
      else:
        value = False
    elif value:
      value = True
    else:
      value = False


    return value