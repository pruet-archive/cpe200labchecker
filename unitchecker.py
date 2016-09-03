#!/bin/env python3

import os
import shutil
import glob
import subprocess
from github import Github
from git import Repo
import configparser
from pprint import pprint

class UnitChecker:
  config = configparser.ConfigParser()
  def __init__(self):
    self.config.read('config.ini')

  def join(self, path1, path2):
    return os.path.join(path1, path2)

  def process_unittest(self, path) :
    pass

  def remove_folder(self, path):
    if os.path.exists(path):
      shutil.rmtree(path)

  def get_lab_list(self, path):
    if not os.path.exists(path):
      return null
    return glob.glob(self.join(path, 'lab*'))

  def get_hw_list(self, path):
    if not os.path.exists(path):
      return null
    return glob.glob(self.join(path, 'hw*'))

  def get_file_list(self, path):
    if not os.path.exists(path):
      return null
    return glob.glob(self.join(path, '*.java'))

  def compile_java(self, path, file):
    junit = str(self.config['java']['junit_lib'])
    java_path = str(self.config['java']['java_bin_path'])
    cmd = java_path + '/javac -cp ' + junit + ':' + path + ' ' + file
    proc = subprocess.Popen(cmd, shell=True)
  
  def run_unittest(self, path, java_class):
    #FIXME make assumption here that file will ended with .java
    junit = str(self.config['java']['junit_lib'])
    java_path = str(self.config['java']['java_bin_path'])
    command = [self.join(java_path,'java') , '-cp', junit + ':' + path, 'org.junit.runner.JUnitCore',java_class]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=None, shell=False)
    return(process.communicate()[0])

  def process_git(self, org, repo):
    gitUser = str(self.config['authen']['user'])
    gitToken = str(self.config['authen']['token'])

    gh = Github(login_or_token=gitToken)

    prs = gh.get_organization(org).get_repo(repo).get_pulls()
    result = {}
    for pr in prs:
      result['title'] = pr.title
      #print(pr.title)
      result['git_url'] = pr.head.repo.git_url
      #print(pr.head.repo.git_url)
      local_path = self.join('/tmp', str(pr.head.repo.id))
      #self.remove_folder(local_path)
      #Repo.clone_from(pr.head.repo.git_url, local_path)
      result['tests'] = {}
      if repo.endswith('lab'):
        dir_list = self.get_lab_list(local_path)
      else:
        dir_list = self.get_hw_list(local_path)
      for dir in dir_list:
        src_dir = self.join(dir, 'src')
        for java_file in self.get_file_list(src_dir):
          self.compile_java(src_dir, java_file)
        for java_file in self.get_file_list(src_dir):
          if java_file.endswith('Test.java'):
            (head, tail) = os.path.split(java_file)
            java_class = tail[:-5]
            ret_list = self.run_unittest(src_dir, java_class).decode('utf-8').split('\n')
            if ret_list[3].endswith('failures:'):
              result['tests'][java_class] = ret_list[3]
            else:
              result['tests'][java_class] = ret_list[4]
            #print(ret_list[4])
      break
    return(result)
uc = UnitChecker()
result = uc.process_git('cpe200-159-sec1','cpe200-week1-lab')
pprint(result)