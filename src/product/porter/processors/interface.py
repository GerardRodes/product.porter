# -*- coding: utf-8 -*-


class IProcessor(object):

  def __init__(self, item, field_name, field_metadata, context, field_data = None, field_map = None):
    """
      item <Plone object>

      field_name <str>
        
      field_metadata <dict>
        field data

      context
        context mode instance

      field_data
        new value to set to the field
    """
    
    self.item  = item
    self.field_name = field_name
    self.field_metadata = field_metadata
    self.field_data = field_data
    self.field_map = field_map
    self.context = context
    self.log = context.log
    self.accessor = getattr(self.item, self.field_metadata['accessor'])


  def extract(self):
    """
      Returns atleast dict with a key value
    """

    return {
      "value": getattr(self.item, self.field_metadata['accessor'])()
    }


  def value(self):
    # From the json data returns the value to set
    # self.field_data mast be setted from mode script
    value = self.field_data['value']
    if 'filter' in self.field_map:
      value = self.field_map['filter'](value)
    return value


  def mutator(self, value):
    if 'mutator' in self.field_metadata:
      # Archetypes
      mutator = getattr(self.item, self.field_metadata['mutator'])
      mutator(value)
    else:
      # Dexterity
      setattr(self.item, self.field_name, value)