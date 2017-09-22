# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView
from product.porter import Importer
from plone import api
import sys, os, traceback


class ImportView(BrowserView):

  def __init__(self, context, request):
    super(ImportView, self).__init__(context, request)

    try:
      self.importer = Importer(
        portal = api.portal.get(),
        mode = 'container',
        root = '/fs-prova/grodes',
        json_path = '/tmp/exporter/ajsolsona/test/data.json',
        output_path = '/tmp/importer/ajsolsona/test')
      
    except Exception as e:
      exc_type, exc_obj, exc_tb = sys.exc_info()
      fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
      print(
        "\nError %s at %s line %s\n%s\n%s" % 
        ( str(exc_type), str(fname), str(exc_tb.tb_lineno), str(e), traceback.print_exc() )
      )


  def __call__(self):
    if hasattr(self, 'importer'):
      return open(self.importer.logger.file.name, 'r').read()
    else:
      return 'error'