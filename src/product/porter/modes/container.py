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
      # Plone object to json
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


  def _import(self, json_data, root, limit = None):
    """
      root
        folder path where to start the creation of files
    """

    if limit:
      total = limit
      self.log("Import limitted to %i objects." % limit)
    else:
      total = json_data["total"]

    try:
      folder = self.portal.unrestrictedTraverse(root)
    except:
      self.log("Container at '%s' doesn't exists, create it manually." % root, exception = True)

    self.processed_objects = 0

    def create_item(item_json, parent):
      # json to Plone object

      if limit and self.processed_objects >= limit:
        return

      item_portal_type = item_json['metadata']['portal_type']
      if item_portal_type != "Plone Site":
        item_id = item_json['metadata']['id']
        created_or_updated = "Created"
        if item_id not in parent:
          # If doesn't exists create object
          parent.invokeFactory(item_portal_type, item_id)
          item = parent[item_id]
          item.reindexObject()

        else:
          item = parent[item_id]
          created_or_updated = "Updated"

        if 'status' in item_json['metadata']:
          status = item_json['metadata']['status']
          for action in self.portal_workflow.listActions(object=item):
            if 'id' in action and 'transition' in action and action['transition'].new_state_id == status['review_state'] and self.portal_workflow.getInfoFor(item, 'review_state') != action['transition'].new_state_id:
              try:
                self.portal_workflow.doActionFor(item, action['id'])
              except:
                t, e = sys.exc_info()[:2]
                self.happens("Something went wront while updating review state:\n%s\nItem json data status:\n%s" % (str(e), str(status)))
                pass

        # Set fields values


        self.processed_objects += 1
        self.log(
          "%i/%i %s item with id: %s" %
          (self.processed_objects, total, created_or_updated, item_id)
        )

      else:
        self.log("This item is a Plone Site, it's childs will be created at the current container: '%s'" % str(parent))
        # If the first item is the Plone Site it will be omitted
        # and all it's children will be created inside the specified root folder
        item = parent
      


      if 'childs' in item_json:
        for child in item_json['childs']:
          create_item(child, item)


    create_item(json_data['data'], folder)