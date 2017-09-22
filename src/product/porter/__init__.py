# -*- coding: utf-8 -*-
"""Init and utils."""


from zope.i18nmessageid import MessageFactory
from product.porter import processors
try:
  from zope.schema import getFieldsInOrder
  from plone.behavior.interfaces import IBehaviorAssignable
  from zope.schema.interfaces import *
  from plone.app.textfield.interfaces import IRichText
  from plone.namedfile.interfaces import *
except:
  print "Can't import dexterity tools"
  pass

_ = MessageFactory('product.porter')
META_TYPES = (
  'ATDocument',
  'ATFolder', 
  'ATEvent',
  'ATFavorite',
  'ATFile',
  'ATImage',
  'ATLink',
  'ATTopic',
  'ATNewsItem',
  'ATBTreeFolder',
  'FieldsetFolder',
  'FormBooleanField',
  'FormCaptchaField',
  'FormCustomScriptAdapter',
  'FormDateField',
  'FormFileField',
  'FormFixedPointField',
  'FormFolder',
  'FormIntegerField',
  'FormLabelField',
  'FormLikertField',
  'FormLinesField',
  'FormMailerAdapter',
  'FormMultiSelectionField',
  'FormPasswordField',
  'FormRichLabelField',
  'FormRichTextField',
  'FormSaveDataAdapter',
  'FormSelectionField',
  'FormStringField',
  'FormTextField',
  'FormThanksPage',
)
IGNORE = "__ignore__"
ALL = "__all__"
DEFAULT_FIELDS_MAP = {
  ALL: {
    "presentation": {"name": IGNORE},
    "rights": {"name": IGNORE},
    "subject": {"name": "subjects"},
    "location": {"name": IGNORE},
    "creation_date": {"name": "created"},
    "effectiveDate": {"name": "effective"},
    "expirationDate": {"name": "expires"},
    "allowDiscussion": { "name": "allow_discussion", "filter": lambda value: value},
    "excludeFromNav": {"name": "exclude_from_nav"},
    "tableContents": {"name": "table_of_contents"},
    "modification_date": {"name": "modified"},
    "immediatelyAddableTypes": {"name": "immediately_addable_types"},
    "locallyAllowedTypes": {"name": "locally_allowed_types"},
    "constrainTypesMode": {"name": "constrain_types_mode"},
  },
}

try:
  # Which processor correspond to each field interface
  # They are ordered from less to most priority
  PROCESSORS = [{
    'name': 'boolean',
    'interfaces': [IBool],
    'fields': []
  },
  {
    'name': 'computed',
    'interfaces': [],
    'fields': []
  },
  {
    'name': 'file',
    'interfaces': [IFile, INamedField, INamedBlobFile],
    'fields': []
  },
  {
    'name': 'image',
    'interfaces': [INamedImage, INamedBlobImage],
    'fields': [],
    'filter': lambda field_instance: hasattr(field_instance, 'getImageSize'),
  },
  {
    'name': 'integer',
    'interfaces': [IInt, IBytesLine, IBytes],
    'fields': []
  },
  {
    'name': 'float',
    'interfaces': [IFloat, IDecimal],
    'fields': []
  },
  {
    'name': 'lines',
    'interfaces': [ITuple, IAbstractSet, IUnorderedCollection, IDict, IList, IIterable, ISet, ISequence, ICollection],
    'fields': []
  },
  {
    'name': 'reference',
    'interfaces': [],
    'fields': ['relatedItems']
  },
  {
    'name': 'string',
    'interfaces': [ISourceText, IURI, INativeStringLine, IASCIILine, ITextLine, IPassword, IId, INativeString, IASCII, IChoice, IText],
    'fields': []
  },
  {
    'name': 'text',
    'interfaces': [IRichText],
    'fields': ['description']
  },
  {
    'name': 'datetime',
    'interfaces': [IDate, ITime, ITimedelta, IDatetime],
    'fields': []
  }]
except:
  print "Can't set dexterity globals"
  pass



# Utils
from product.porter.logger import Logger


def test(condition, true, false = None):
  # Python 2.4 doesn't have ternary operators
  value = condition
  if callable(condition):
    value = condition()

  if value:
    return true
  else:
    return false



def classname_from_modename(name):
  # Given a modename returns its classname
  return "%s%sMode" % (name[0].upper(), name[1:])



def processor_classname_from_field_type(field_type):
  # Given a field_type returns its processor class name
  return "%s%sProcessor" % (field_type[0].upper(), field_type[1:])



def field_processor_factory(context, item, field_name, field_metadata, field_data = None):
  """
    Returns an instance of a field processor for an explicit Plone object

    context
      who is executing the function, must apply IDumper

    item
      Plone object

    field_name
      name of the field

    field_metadata
      metadata from the meta_type, can be found at json_data['metadata'][meta_type]['fields'][field_name]

    field_data
      value and other aspects of the field value
  """
  
  processor_module = getattr(processors, field_metadata['type'], None)

  if processor_module:
    processor_classname = processor_classname_from_field_type(field_metadata['type'])
    ProcessorClass = getattr(processor_module, processor_classname, None)

    if ProcessorClass:
      return ProcessorClass(item, field_name, field_metadata, context, field_data)
    else:
      context.log("Processor class %s not found at %s" % (processor_classname, processor_module.__name__), exception = True)
  else:
    context.log("Processor module %s not found at %s" % (field_metadata['type'], processors.__name__), exception = True)



def parse_field(field_name, field_instance):
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



def research_fields_by_schema(schema):
  # Parses field from archetypes schema
  output = {}
  for field_instance in schema.fields():
    field_name = field_instance.getName()
    if field_name != 'id':
      field = parse_field(field_name, field_instance)
      output[field_name] = field

  return output



def parse_field_dexterity(field_name, field_instance):
  field_type = None
  for processor in PROCESSORS:
    if field_name in processor['fields']:
      field_type = processor['name']
      break

  if field_name == 'image':
    print 'filter'
    print field_instance.getImageSize
    print hasattr(field_instance, 'getImageSize')

  if not field_type:
    for processor in PROCESSORS:
      if 'filter' in processor and processor['filter'](field_instance):
        field_type = processor['name']
      for interface in processor['interfaces']:
        if interface.providedBy(field_instance):
          field_type = processor['name']

  if not field_type:
    raise Exception("Field %s %s doesn't have assigned any processor at variable PROCESSORS at product.porter.__init__.py file" % (field_name, str(field_interface)))

  return {
    'type':     field_type
  }



def researh_fields_dexterity(item):
  # Get fields from schema
  fields = {
    "created": {"type": "datetime"},
    "modified": {"type": "datetime"},
    "immediately_addable_types": {"type": "lines"},
    "locally_allowed_types": {"type": "lines"},
    "constrain_types_mode": {"type": "integer"},
  }
  for field_name, field_instance in getFieldsInOrder(item.getTypeInfo().lookupSchema()):
    fields[field_name] = parse_field_dexterity(field_name, field_instance)

  # Get fields from behaviors
  behavior_assignable = IBehaviorAssignable(item)
  if behavior_assignable:
    behaviors = behavior_assignable.enumerateBehaviors()
    for behavior in behaviors:
      for field_name, field_instance in getFieldsInOrder(behavior.interface):
        fields[field_name] = parse_field_dexterity(field_name, field_instance)

  return fields



def get_meta_type_fields_map(meta_type, fields_map):
  meta_type_fields_map = fields_map.get(ALL, {})
  meta_type_fields_map.update(fields_map.get(meta_type, {}))
  return meta_type_fields_map



def get_field_map(meta_type, field_name, fields_map):
  return get_meta_type_fields_map(meta_type, fields_map).get(field_name, {})



# Parts
from product.porter.modes import *



# Tools
from product.porter.importer import Importer
from product.porter.exporter import Exporter