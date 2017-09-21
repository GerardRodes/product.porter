# -*- coding: utf-8 -*-

from product.porter import *
from datetime import datetime
import sys
try:
  import json
except:
  import simplejson as json


class Exporter:

  def __init__(self, portal, mode, output_path = '/tmp/exporter', indent = None, logger_level = 0, **kwargs):
    """
      portal
        portal object

      mode
        export mode

      output_path
        where to export the data and save the logs

      indent
        json indent, if None returns it without format

      kwargs
        each mode could require different parameters
    """

    self.init_time = datetime.now()
    self.indent = indent

    self.splitted_output_path = output_path.split('/')
    if self.splitted_output_path[:-1][0].endswith(".json"):
      self.filename = self.splitted_output_path[-1:][0]
      self.output_path = '/'.join(self.splitted_output_path[:-1])
    else:
      self.filename = "data.json"
      self.output_path = output_path

    self.logger = Logger(self.output_path, level = logger_level)
    self.log = self.logger.log

    self.json_file_path = '/'.join(self.output_path.split('/') + [self.filename])
    self.json_file = open(self.json_file_path, 'w+')
    self.json_file.close()

    self.log('Initialized', print_time = True)

    self.portal = portal


    # EXECUTING EXPORT MODE

    modename = mode.lower()
    mode_module = getattr(modes, modename, None)

    if mode_module:
      self.log('Executing export in mode %s' % modename)

      classname = classname_from_modename(mode.lower())
      ModeClass = getattr(mode_module, classname, None)

      if ModeClass:
        mode_instance = ModeClass(portal, self.log)

        json_data = mode_instance._export(**kwargs)
        output = {
          "data": json_data,
          "total": mode_instance.dumpped_objects,
          "metadata": getattr(mode_instance, 'meta_types')
        }
        try:
          json_file = open(self.json_file_path, 'w+')
          json.dump(output, json_file, indent=self.indent)
          json_file.close()
        except:
          t, e = sys.exc_info()[:2]
          self.log(e)
          self.log("Error while saving as json, trying save as txt...")
          txt_file = open(self.json_file_path.replace('.json', '.txt'), 'w+')
          txt_file.write(str(output))
          txt_file.close()


      else:
        self.log('Class `%s` not found at %s' % (classname, mode_module.__name__))
    else:
      self.log('Module `%s` not found at %s' % (modename, modes.__name__))

    self.log('Finished in %s' % (datetime.now() - self.init_time), print_time = True)