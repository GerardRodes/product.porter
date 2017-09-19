# -*- coding: utf-8 -*-
"""Init and utils."""


from zope.i18nmessageid import MessageFactory

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
  # Given a modename returns its classname
  return "%s%sProcessor" % (field_type[0].upper(), field_type[1:])



# Parts
from product.porter.modes import *



# Tools
from product.porter.importer import Importer
from product.porter.exporter import Exporter