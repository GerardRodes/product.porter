# -*- coding: utf-8 -*-

from datetime import datetime
import os, sys, unicodedata


class Logger:

  def __init__(self, folder_path, level = 0, print_time = False):
    """
      folder_path
        folder where to create the log.txt file

      print_time
        if True each line will be prepend with the time when it's printted

      level
        a message will only be printted if its level is equal or less than the level of the logger
        by default the level of the logger is 0 and the level of a message is 0 too
    """
    self.folder_path = folder_path
    self.file_path = '/'.join(folder_path.split('/') + ['log.txt'])
    self.print_time = print_time
    self.level = level

    if not os.path.exists(self.folder_path):
      os.makedirs(self.folder_path)

    self.file = open(self.file_path, 'w+')
    self.file.close()


  def log(self, message, level = 0, print_time = None, exception = False):
    if level <= self.level:

      if print_time == None:
        print_time = self.print_time

      output = ''

      if print_time:
        output += '%s -- ' % datetime.now().strftime('%H:%M:%S')

      if isinstance(message, unicode):
        message = unicodedata.normalize('NFKD', message).encode('ascii','ignore')

      output += str(message) + '\n'

      # print at console
      sys.stdout.write(output)
      sys.stdout.flush()


      # print at file
      log_file = open(self.file.name, 'a')
      log_file.write(output)
      log_file.close()

    if exception:
      raise Exception(message)