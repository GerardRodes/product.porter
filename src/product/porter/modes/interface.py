# -*- coding: utf-8 -*-

class IMode:

  def __init__(self, portal, log):
    self.portal = portal
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