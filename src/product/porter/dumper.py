# -*- coding: utf-8 -*-

from Products.CMFCore.interfaces import IFolderish
from Products.CMFCore.utils import getToolByName
from product.porter import processors, processor_classname_from_field_type



class IDumper:
  """
    Provides the ability to dump portal items to json
  """

  def __init__(self, portal):
    self.portal = portal
    self.portal_workflow = getToolByName(self.portal, "portal_workflow")
    self.meta_types = {}


  def dump_data(self, item):
    # Given a Plone object dumps it to json

    item_json = {
      "metadata": {
        'meta_type':   item.meta_type,
        'portal_type': item.portal_type,
        'id':          item.getId(),
        'path':        '/'.join(item.getPhysicalPath()),
        'folderish':   str(IFolderish.providedBy(item)),
      }
    }


    chain = self.portal_workflow.getChainFor(item)
    if len(chain) > 0:
      state = self.portal_workflow.getStatusOf(chain[0], item)
      if state and 'review_state' in state:
        item_json['metadata']['review_state'] = state['review_state']

    if hasattr(item, 'UID'):
      item_json['metadata']['uid'] = item.UID()


    if item.meta_type != 'Plone Site':
      item_json['fields'] = {}

      if item.meta_type not in self.meta_types.keys():
        self.log('Adding new meta_type %s' % item.meta_type, 1)
        self.meta_types[item.meta_type] = {
          'meta_type': item.meta_type,
          'fields':    self.research_fields_by_schema(item.schema),
        }

      for field_name in self.meta_types[item.meta_type]['fields'].keys():
        field_data = self.meta_types[item.meta_type]['fields'][field_name]
        item_json['fields'][field_name] = self.dump_field(item, field_name, field_data)

    return item_json


  def research_fields_by_schema(self, schema):
    output = {}
    for field_instance in schema.fields():
      field_name = field_instance.getName()
      if field_name != 'id':
        field = self.parse_field(field_name, field_instance)
        output[field_name] = field
        self.log('Added field width data: ' + str(field), level=1)

    return output


  def parse_field(self, field_name, field_instance):
    field = {
      'type':     field_instance._properties['type'],
      'accessor': field_instance.accessor,
      'mutator':  field_instance.mutator
    }

    if not field['accessor']:
      field['accessor'] = 'get' + field_name[0].upper() + field_name[1:]

    if not field['mutator']:
      field['mutator'] = 'set' + field_name[0].upper() + field_name[1:]

    return field


  def dump_field(self, item, field_name, field_data):
    processor_module = getattr(processors, field_data['type'], None)
    if processor_module:
      processor_classname = processor_classname_from_field_type(field_data['type'])
      ProcessorClass = getattr(processor_module, processor_classname, None)

      if ProcessorClass:
        processor_instance = ProcessorClass(item, field_name, field_data, self)
        data = processor_instance.extract()

        if not isinstance(data, dict) or 'value' not in data:
          msg = "Processor <%s> `extract` method must return a dictionary with a keyword named `value` containing the field value.\nInstead it returned this data: %s" % (processor_classname, str(data))
          self.log(msg)
          raise Exception(msg)
        else:
          return data
      else:
        self.log("Processor class %s not found at %s" % (processor_classname, processor_module.__name__))
    else:
      self.log("Processor module %s not found at %s" % (field_data['type'], processors.__name__))