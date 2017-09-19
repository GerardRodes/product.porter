# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from product.porter.modes.interface import IMode
from product.porter.dumper import IDumper
from Products.CMFCore.interfaces import IFolderish
import os



class ContainerMode(IMode, IDumper):

  def __init__(self, portal, log):
    IMode.__init__(self, portal, log)
    IDumper.__init__(self, portal)
    self.catalog = self.portal.portal_catalog


  def _export(self, root, content_filter = {}, limit = None, download_files = True):
    """
      root
        path of the folder where to start
        includes the folder itself and all its children

      content_filter
        filter getFolderContents results

      limit
        max results

      download_files
        if True files are downloaded at {output_path}/files
    """
    self.download_files = download_files
    if self.download_files:
      self.output_folder = '/'.join(self.log.im_self.folder_path.split('/') + ['files'])
      if not os.path.exists(self.output_folder):
        os.makedirs(self.output_folder)

    self.dumpped_objects = 0
    if not limit:
      self.guessed_coincidences = len( self.catalog({
        "path": root
      }.update(content_filter)) )
      self.log("Found %i coincidences, could be less results at exported data." % self.guessed_coincidences)
    else:
      self.guessed_coincidences = limit
      self.log("Result limited to %i items." % self.guessed_coincidences)


    item = self.portal.unrestrictedTraverse(root)

    def dump_item(item):
      if limit and self.dumpped_objects >= limit:
        return

      item_json = self.dump_data(item)
      self.dumpped_objects += 1
      self.log(
        '%i/%i Dumpped new item with id: %s' %
        (self.dumpped_objects, self.guessed_coincidences, item.getId())
      )

      if IFolderish.providedBy(item):
        item_json['childs'] = []
        childs = item.getFolderContents(content_filter)
        if childs:
          for child in childs:
            child_json = dump_item(child.getObject())
            if child_json:
              item_json['childs'].append(child_json)

      return item_json


    return dump_item(item)