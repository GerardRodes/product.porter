# -*- coding: utf-8 -*-
"""Init and utils."""


from zope.i18nmessageid import MessageFactory
from product.porter import processors

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
  output = {}
  for field_instance in schema.fields():
    field_name = field_instance.getName()
    if field_name != 'id':
      field = parse_field(field_name, field_instance)
      output[field_name] = field

  return output


# Parts
from product.porter.modes import *



# Tools
from product.porter.importer import Importer
from product.porter.exporter import Exporter