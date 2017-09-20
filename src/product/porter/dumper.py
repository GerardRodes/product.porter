# -*- coding: utf-8 -*-

from Products.CMFCore.interfaces import IFolderish
from Products.CMFCore.utils import getToolByName
from product.porter import processors, processor_classname_from_field_type, research_fields_by_schema
from product.porter.processors.datetime import parse_datetime


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
        item_json['metadata']['status'] = state
        item_json['metadata']['status']['time'] = parse_datetime(item_json['metadata']['status']['time'])["value"]
        item_json['metadata']['status']['workflow'] = chain[0]

    if hasattr(item, 'UID'):
      item_json['metadata']['uid'] = item.UID()


    if item.meta_type != 'Plone Site':
      item_json['fields'] = {}

      if item.meta_type not in self.meta_types.keys():
        self.log('Adding new meta_type %s' % item.meta_type, 1)
        self.meta_types[item.meta_type] = {
          'portal_type': getattr(item, 'portal_type', None),
          'fields':    research_fields_by_schema(item.schema),
        }

      for field_name in self.meta_types[item.meta_type]['fields'].keys():
        field_data = self.meta_types[item.meta_type]['fields'][field_name]
        item_json['fields'][field_name] = self.dump_field(item, field_name, field_data)

    return item_json


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