# -*- coding: utf-8 -*-


class IProcessor:

  def __init__(self, item, field_name, field_data, dumper):
    """
      item <Plone object>

      field_name <str>
        
      field_data <dict>
        field data

      dumper
        dumper mode instance
    """
    self.item  = item
    self.field_name = field_name
    self.field_data = field_data
    self.dumper = dumper
    self.log = dumper.log


  def extract(self):
    """
      Returns atleast dict with a key value
    """
    return {
      "value": getattr(self.item, self.field_data['accessor'])()
    }


  def insert(self):
    """
      Sets the field value to the item
    """