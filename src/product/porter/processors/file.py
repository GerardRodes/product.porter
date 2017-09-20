# -*- coding: utf-8 -*-

from product.porter.processors.interface import IProcessor
import os, re, filecmp, hashlib


def md5(file_path):
  # returns hash of file from file_path
  hash_md5 = hashlib.md5()
  file = open(file_path, "rb")
  for chunk in iter(lambda: file.read(4096), ""):
    hash_md5.update(chunk)
  file.close()
  return hash_md5.hexdigest()


def upgrade_copy_name(name):
  # Adds a number to the start of the file indicating the number of copies that exists
  number = -1
  if name[0] == "(":
    matches = re.match(r"\(([\d]+)\)", name, flags=0)
    if matches:
      number = int(matches.group(1))
      current_prefix = "(%i) " % number
      name = name.replace(current_prefix, "")

  return "(%i) %s" % (number + 1, name)


def file_contains(file_path, data):
  # Returns True if a file contains the data
  file = open(file_path, 'r')
  file_data = file.read()
  file.close()

  return 


FILE_HASH = {}


class FileProcessor(IProcessor):
  
  def extract(self):
    global FILE_HASH

    value = self.get_data()
    if not value:
      return {
        "value": None
      }

    size = len(str(value))
    if size:
      filename     = self.item.getFilename(self.field_name) or self.item.getId()
      content_type = self.item.getContentType(self.field_name)
      extension    = content_type.split('/')[1]
      temp_name    = filename
      self.log('Creating file %s, size: %s ' % (temp_name, str(size)), 1)

      if self.dumper.download_files:
        file_path = '/'.join(self.dumper.output_folder.split('/') + [temp_name])

        while os.path.isfile(file_path):
          # If file exists check if is the same file or not
          self.log("File `%s` exists" % file_path, 1)
          if temp_name not in FILE_HASH:
            # If hash doesn't exists create it
            hash_md5  = hashlib.md5()
            hash_md5.update(value)
            FILE_HASH[temp_name] = hash_md5.hexdigest()

          if FILE_HASH[temp_name] == md5(file_path):
            # If new file name created exists too but contents are the same
            # stop the loop and provide the current file_path and temp_name as accepted
            self.log("File `%s` has the same content, we are going to use it instead." % file_path, 1)
            break
          temp_name = upgrade_copy_name(temp_name)
          file_path = '/'.join(self.dumper.output_folder.split('/') + [temp_name])


        file_relative_path = '/'.join(['.'] + ['files', temp_name])
        file = open(file_path, 'w+')
        file.write(value)
        file.close()

    return {
      "value": file_relative_path,
      "size": size,
      "content_type": content_type,
      "filename":filename ,
      "download_url": self.item.absolute_url() + '/at_download/' + self.field_name,
    }


  def get_data(self):
    return str(getattr(self.item, self.field_data['accessor'])())