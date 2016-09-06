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
    #self.config.read('/var/www/grading/config.ini')
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
      return None
    return glob.glob(self.join(path, 'lab*'))

  def get_hw_list(self, path):
    if not os.path.exists(path):
      return None
    return glob.glob(self.join(path, 'hw*'))

  def get_file_list(self, path):
    if not os.path.exists(path):
      return None
    return glob.glob(self.join(path, '*.java'))

  def compile_java(self, path, file):
    FNULL = open(os.devnull, 'w')
    junit = str(self.config['java']['junit_lib'])
    java_path = str(self.config['java']['java_bin_path'])
    command = [self.join(java_path,'javac'), '-cp', junit + ':' + path, file]
    proc = subprocess.Popen(command, stdout=FNULL, stderr=FNULL, shell=False)
    proc.wait()
  
  def run_unittest(self, path, java_class):
    #FIXME make assumption here that file will ended with .java
    FNULL = open(os.devnull, 'w')
    junit = str(self.config['java']['junit_lib'])
    java_path = str(self.config['java']['java_bin_path'])
    command = [self.join(java_path,'java') , '-cp', path + ':' + junit, 'org.junit.runner.JUnitCore',java_class]
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=FNULL, shell=False)
    proc.wait()
    return(proc.communicate()[0])

  def process_pullrequest(self, pr, repo):
    result = {}
    result['title'] = pr.title
    result['git_url'] = pr.head.repo.git_url
    local_path = self.join('/tmp', str(pr.head.repo.id))
    #id = str(pr.head.repo.id)
    #if id != '66341762':
    #  continue;
    self.remove_folder(local_path)
    Repo.clone_from(pr.head.repo.git_url, local_path)
    result['tests'] = {}
    if repo.endswith('lab'):
      dir_list = self.get_lab_list(local_path)
    else:
      dir_list = self.get_hw_list(local_path)
    if dir_list is None:
      return None
    for dir in dir_list:
      src_dir = self.join(dir, 'src')
      src_code_dir = self.join(src_dir, 'cpe200')
      for java_file in self.get_file_list(src_code_dir):
        self.compile_java(src_dir, java_file)
      src_test_dir = self.join(src_dir, 'cpe200Test')
      src_test_prefix = 'cpe200Test'
      if not os.path.exists(src_test_dir):
        src_test_dir = self.join(src_dir, 'cpe200')
        src_test_prefix = 'cpe200'
      for java_file in self.get_file_list(src_test_dir):
        self.compile_java(src_dir, java_file)
      for java_file in self.get_file_list(src_test_dir):
        if java_file.endswith('Test.java'):
          (head, tail) = os.path.split(java_file)
          java_class = src_test_prefix + '.' + tail[:-5]
          ret_list = self.run_unittest(src_dir, java_class).decode('utf-8').split('\n')
          if ret_list[4].startswith('OK'):
            result['tests'][java_class] = 'OK'
          else:
            result['tests'][java_class] = 'FAIL'
    return(result)

  def process_git(self, org, repo):
    gitUser = str(self.config['authen']['user'])
    gitToken = str(self.config['authen']['token'])

    gh = Github(login_or_token=gitToken)

    prs = gh.get_organization(org).get_repo(repo).get_pulls()
    return prs

#uc = UnitChecker()
#org = 'cpe200-159-sec1'
#repo = 'cpe200-week3-lab'
#prs = uc.process_git(org, repo)
#for pr in prs:
#  result = uc.process_pullrequest(pr, repo)
#  pprint(result)
#  break
