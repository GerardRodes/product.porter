# -*- coding: utf-8 -*-

from product.porter.processors.interface import IProcessor
import time

FILE_COUNT = 0

class FileProcessor(IProcessor):
  
  def extract(self):
    global FILE_COUNT

    value = self.get_data()
    if not value:
      return {
        "value": None
      }

    size = len(str(value))
    if size:
      self.log('File size: ' + str(size), 1)
      filename     = self.item.getFilename(self.field_name) or self.item.getId()
      timestamp    = str(int(round(time.time())*1000))
      content_type = self.item.getContentType(self.field_name)
      extension    = content_type.split('/')[1]
      temp_name    = str(FILE_COUNT) + timestamp + '.' + extension

      FILE_COUNT += 1

      if self.dumper.download_files:
        file_relative_path = '/'.join(['.'] + ['files', temp_name])
        file_path = '/'.join(self.dumper.output_folder.split('/') + [temp_name])
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