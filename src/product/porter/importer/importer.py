# -*- coding: utf-8 -*-

from Products.CMFCore.utils import getToolByName
from product.porter import *
from datetime import datetime
import sys
try:
  import json
except:
  import simplejson as json



class Importer:

  def __init__(self, portal, mode, json_path, output_path = '/tmp/importer', indent = None, logger_level = 0, check_integrity = True, **kwargs):
    """
      portal
        portal object

      mode
        import mode

      json_path
        json with the exported data

      indent
        json indent, if None returns it without format

      kwargs
        each mode could require different parameters

      output_path
        folder where to save the logs

      check_integrity
        whether to check metdata integrity or not
    """

    self.init_time = datetime.now()
    self.indent = indent

    self.output_path = output_path

    self.logger = Logger(self.output_path, level = logger_level)
    self.log = self.logger.log

    self.json_file_path = json_path
    self.json_file = open(self.json_file_path, 'r')
    self.json_data = json.load(self.json_file)

    self.log('Initialized', print_time = True)

    self.portal = portal


    # CHECK INTEGRITY
    #
    # Before starting with the import we are going to check the integrity of the
    # json data with the portal, check if all the portal types which we are going to
    # import are installed in the current portal and have the same field (or they coincide
    # with the provided field mapping)

    if check_integrity and 'metadata' in self.json_data:
      self.log("Cheking metadata integrity...")

      portal_types_tool = getToolByName(self.portal, "portal_types")
      portal_factory_tool = getToolByName(self.portal, 'portal_factory')
      portal_types = portal_types_tool.listContentTypes()

      tempname = 0
      items_ids = [item[0] for item in self.portal.contentItems()]
      while str(tempname) in items_ids:
        tempname += 1

      tempname = str(tempname)

      for meta_type in self.json_data['metadata'].keys():
        meta_type_data = self.json_data['metadata'][meta_type]
        portal_type = meta_type_data['portal_type']

        if portal_type not in portal_types:
          self.log("%s isn't installed on the portal, can't continue with the process.\n\
            This is a list of the currently installed content types:\n%s" % (meta_type, ', '.join(portal_types)), exception = True)

        self.portal.invokeFactory(portal_type, tempname)
        portal_schema_fields = research_fields_by_schema(self.portal[tempname].schema)
        
        for field in meta_type_data['fields']:
          if field in portal_schema_fields:
            json_field_type = meta_type_data['fields'][field].get('type', 'no type assigned on json')
            portal_field_type = portal_schema_fields[field].get('type', 'no type assigned on portal')
            if json_field_type != portal_field_type:
              self.log("%s field doesn't have the same type on portal.\n\
                json data: field_type:%s\nportal data: field_type:%s" % (field, json_field_type, portal_field_type), exception = True)
          else:
            self.log("%s field doesn't exists on portal schema content type installed. Can't continue." % field, exception = True)

        self.portal.manage_delObjects([tempname])
        self.log("%s integrity correct." % portal_type)

    elif check_integrity:
      self.log("No metadata provided about the portal types, it should be at the json as a key named 'metadata'", exception = True)
    else:
      self.log("WARNING: Not checking metadata integrity. Set Importer parameter 'check_integrity' to True")

    if check_integrity:
      self.log("Metadata integrity correct.")


    # EXECUTING IMPORT MODE

    modename = mode.lower()
    mode_module = getattr(modes, modename, None)

    if mode_module:
      self.log('Executing import in mode %s' % modename)

      classname = classname_from_modename(mode.lower())
      ModeClass = getattr(mode_module, classname, None)

      if ModeClass:
        mode_instance = ModeClass(portal, self.log)
        import_folder = '/'.join( self.json_file_path.split('/')[:-1] )
        mode_instance._import(self.json_data, import_folder, **kwargs)

      else:
        self.log('Class `%s` not found at %s' % (classname, mode_module.__name__))
    else:
      self.log('Module `%s` not found at %s' % (modename, modes.__name__))

    self.log('Finished in %s' % (datetime.now() - self.init_time), print_time = True)