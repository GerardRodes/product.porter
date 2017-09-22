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

  def __init__(self, portal, mode, json_path, fields_map = {}, framework = 'dexterity', output_path = '/tmp/importer', indent = None, logger_level = 0, check_integrity = True, **kwargs):
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

      framework
        whether to import as archetypes or dexterity
        must be "dexterity" or "archetypes"

      fields_map
        = {
          "MetaType": {
            "json_fieldname": "metatype field name" if value is "__ignore__" field will be ignored
          }
        }
    """

    self.init_time = datetime.now()
    self.indent = indent
    self.framework = framework.lower()
    self.fields_map = fields_map

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
      portal_types = portal_types_tool.listContentTypes()

      instance_tempname = 0
      items_ids = [item[0] for item in self.portal.contentItems()]
      while str(instance_tempname) in items_ids:
        instance_tempname += 1

      instance_tempname = str(instance_tempname)

      for meta_type in self.json_data['metadata'].keys():
        meta_type_json_data = self.json_data['metadata'][meta_type]
        portal_type = meta_type_json_data['portal_type']

        if portal_type not in portal_types:
          self.log("%s isn't installed on the portal, can't continue with the process.\n\
            This is a list of the currently installed content types:\n%s" % (meta_type, ', '.join(portal_types)), exception = True)

        if self.framework == "archetypes":
          type_info = portal_types_tool.getTypeInfo(portal_type)
          temp_instance = type_info._constructInstance(self.portal, instance_tempname)
          portal_schema_fields = research_fields_by_schema(temp_instance.schema)

        elif self.framework == "dexterity":
          from plone.dexterity.utils import createContentInContainer
          temp_instance = createContentInContainer(self.portal, portal_type, id=instance_tempname, checkConstraints=False)
          print 'Created instance of ', portal_type, instance_tempname, temp_instance.id
          portal_schema_fields = researh_fields_dexterity(temp_instance)

        for field_name in meta_type_json_data['fields']:
          # Field name becomes the field map or if its IGNORE ignore field
          field_map = get_field_map(meta_type, field_name, self.fields_map)
          if field_map.get("name", None) == IGNORE:
            self.log("Field %s of meta type %s has value None at field map, ignoring." % (field_name, meta_type), 1)
            continue
          else:
            field_name_json = field_name
            field_name = field_map.get("name", field_name)

          if field_name in portal_schema_fields:
            json_field_type = meta_type_json_data['fields'][field_name_json].get('type', 'no type assigned on json')
            portal_field_type = portal_schema_fields[field_name].get('type', 'no type assigned on portal')
            if json_field_type != portal_field_type and 'filter' not in field_map:
              self.log("%s field of meta type %s doesn't have the same type on portal.\njson data: field_type:%s\nportal data: field_type:%s" %
                (field_name, meta_type, json_field_type, portal_field_type), exception = True)
          else:
            self.log("%s field doesn't exists on content type %s installed. Can't continue." % (field_name, meta_type), exception = True)

        self.portal.manage_delObjects([instance_tempname])
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
        mode_instance._import(self.json_data, import_folder, self.fields_map, **kwargs)

      else:
        self.log('Class `%s` not found at %s' % (classname, mode_module.__name__))
    else:
      self.log('Module `%s` not found at %s' % (modename, modes.__name__))

    self.log('Finished in %s' % (datetime.now() - self.init_time), print_time = True)