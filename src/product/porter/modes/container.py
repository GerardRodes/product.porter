# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from product.porter.modes.interface import IMode
from product.porter import field_processor_factory
from Products.CMFCore.interfaces import IFolderish
import os


class ContainerMode(IMode):

  def __init__(self, portal, log):
    IMode.__init__(self, portal, log)
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
        "path": {
          "query": root
        }
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


  def _import(self, json_data, import_folder, root, limit = None):
    """
      json_data
        it comes from the Importer, don't worry about it (It's your json_path loaded)

      import_folder
        path of the folder where the json file is located

      root
        folder path where to start the creation of files
    """
    self.json_data = json_data
    self.import_folder = import_folder

    if limit:
      total = limit
      self.log("Import limitted to %i objects." % limit)
    else:
      total = self.json_data["total"]

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
      item_meta_type   = item_json['metadata']['meta_type']

      if item_portal_type != "Plone Site":
        item_id = item_json['metadata']['id']
        item_uid = item_json['metadata']['uid']
        created_or_updated = "Created"

        if item_id not in parent:
          # If doesn't exists create object
          parent.invokeFactory(item_portal_type, item_id)
          item = parent[item_id]
          item.reindexObject()
        else:
          # Else get it to update if needed
          item = parent[item_id]
          created_or_updated = "Updated"

        try:
          same_uid_objects = self.portal.reference_catalog.lookupObject(item_uid)
          if item_uid != item.UID() and not same_uid_objects:
            item._setUID(item_uid)
            item.reindexObject()
            self.log("UID %s setted for %s." % (item_uid, str(item)), 1)
        except:
          self.log("Couldn't set UID %s for %s." % (item_uid, str(item)), 1)
          pass


        # Setting review_state
        if 'status' in item_json['metadata']:
          status = item_json['metadata']['status']
          for action in self.portal_workflow.listActions(object=item):
            if 'id' in action and 'transition' in action and action['transition'].new_state_id == status['review_state'] and self.portal_workflow.getInfoFor(item, 'review_state') != action['transition'].new_state_id:
              try:
                self.portal_workflow.doActionFor(item, action['id'])
              except:
                t, e = sys.exc_info()[:2]
                self.log("Something went wront while updating review state:\n%s\nItem json data status:\n%s" % (str(e), str(status)))
                pass


        # Setting fields values
        if 'fields' in item_json:
          for field_name in item_json['fields']:
            field_metadata = self.json_data['metadata'][item_meta_type]['fields'][field_name]
            field_data     = item_json['fields'][field_name]
            processor_instance = field_processor_factory(self, item, field_name, field_metadata, field_data)

            # extract returns the current value of the field setted at the plone object
            # value returns the new value of the field to set
            current_value = processor_instance.accessor()
            new_value = processor_instance.value()

            try:
              if type(new_value) != type(current_value):
                if isinstance(new_value, str):
                    current_value = str(current_value)
            except:
              pass

            if new_value != current_value:
              # mutator sets the value to the field
              processor_instance.mutator(new_value)
              self.log("Field %s value setted." % field_name, 1)
            else:
              self.log("Field %s value ignored.\ncurrent value:%s\nnew value:%s" %
                (field_name, str(current_value), str(new_value)), 1)


        item.reindexObject()

        self.processed_objects += 1
        self.log(
          "%i/%i %s item with id: %s" %
          (self.processed_objects, total, created_or_updated, item_id)
        )

      else:
        # If the first item is the Plone Site it will be omitted
        # and all it's children will be created inside the specified root folder
        self.log("This item is a Plone Site, it's childs will be created at the current container: '%s'" % str(parent))
        item = parent
      

      # And the power of recursion for its childs!
      if 'childs' in item_json:
        for child in item_json['childs']:
          create_item(child, item)


    create_item(self.json_data['data'], folder)