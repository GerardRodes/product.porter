# -*- coding: utf-8 -*-
from product.porter.dumper import IDumper

class IMode(IDumper):

  def __init__(self, portal, log):
    IDumper.__init__(self, portal)
    self.log = log


  def _export(self):
    """
      Given some custom params returns a json with the data
    """
    return None


  def _import(self, json_data):
    """
      Given some custom params and a json creates content on the site
    """
    return None