import os
import jenkins
import xml.etree.ElementTree as ET
from git import Repo
from pathlib import Path

STUB_GIT_URL = "STUB_GIT_URL"
STUB_JENKINS_PATH = "STUB_JENKINS_PATH"
STUB_TOKEN = "STUB_TOKEN"

def read_xml(path_to_config_file):
    tree = ET.parse(path_to_config_file)
    tree.findtext()
    return tree

# 2DO Better to insert CONSTANTS for each replace and use string replace.
def xml_modify(tree, jenkins_path, remote_git, token_val):
    definition = tree.find('definition')
    script_path = definition.find("scriptPath")
    script_path.text = jenkins_path

    scm = definition.find("scm")
    userRemoteConfig = scm.find("userRemoteConfigs")
    url_plugin = userRemoteConfig.find("hudson.plugins.git.UserRemoteConfig")
    url = url_plugin.find("url")
    url.text = remote_git

    properties = tree.find('properties')
    print(properties)
    PipelineTriggersJobProperty = properties.find('org.jenkinsci.plugins.workflow.job.properties.PipelineTriggersJobProperty')
    print(PipelineTriggersJobProperty)
    triggers = PipelineTriggersJobProperty.find('triggers')
    GenericTrigger = triggers.find('org.jenkinsci.plugins.gwt.GenericTrigger')
    print(triggers)
    token = GenericTrigger.find('token')
    token.text = token_val
    print(token_val)


def xml_modifyStr(path, jenkins_path, remote_git, token_val):
   with open(path, 'r') as file:
      data = file.read()
      data = data.replace(STUB_JENKINS_PATH, jenkins_path)
      data = data.replace(STUB_GIT_URL, remote_git)
      data = data.replace(STUB_TOKEN, token_val)
      return data


def xml_toStr(tree):
    root = tree.getroot()
    return ET.tostring(root, encoding='utf8', method='xml').decode()

def read_jobs(J_SERVER):
   jobs = J_SERVER.get_jobs()
   for job in jobs:
      try: 
         job_name = job['name']
         job_config = J_SERVER.get_job_config(job_name)
         job_dir = "jobs"
         if not os.path.exists(job_dir):
            os.mkdir(job_dir)
         print("Reading job: ",job_name)
         job_file = open(job_dir + '/' + job_name + '.xml', 'w')
         job_file.write(job_config)
         job_file.close()
      except Exception as e: 
         print("Error job: ",job_name, e)


def main():
   J_ID = os.environ['JENKINS_ID']
   J_TOKEN = os.environ['JENKINS_TOKEN']
   J_ADDR = os.environ['JENKINS_URL']
   J_URL = 'http://%s:%s@%s' % (J_ID, J_TOKEN, J_ADDR)
   J_SERVER =  jenkins.Jenkins(J_URL)
   # read_jobs(J_SERVER)
   repo = Repo(search_parent_directories=True)
   
   repo_url = repo.remotes.origin.url
   if repo_url.startswith("git@"):
      repo_url = repo_url.replace(":", "/")
      repo_url = repo_url.replace("git@", "https://")

   repo_name = repo.remotes.origin.url.split('.git')[0].split('/')[-1]
   base_testdir = Path(repo.git_dir).parent
   
   test_type = "jenkins_k8s"
   test_template = "fixtures/pipeline_template_cfg.xml"
   # test_template = "jobs/testing_mock_repo_old.xml"

   test_dir = ".."
   test_dirs = Path(test_dir).glob("*test*")

   for dir in test_dirs:

      try:
         folder_name = repo_name
         sub_folder_name = os.path.join(folder_name, test_type)
         test_name = '%s/%s' % (sub_folder_name, dir.stem)
         jenkins_path = '%s/Jenkinsfile' % (dir.stem)
         jenkins_path = os.path.join(test_type, dir.stem, "Jenkinsfile")
         # xml_tree = read_xml(test_template)
         # xml_modify(xml_tree, jenkins_path, repo_url, dir.stem)
         # xml_str =  xml_toStr(xml_tree)
         xml_str = xml_modifyStr(test_template, jenkins_path, repo_url, dir.stem)
         J_SERVER.create_folder(folder_name, ignore_failures=True)
         J_SERVER.create_folder(sub_folder_name, ignore_failures=True)

         if (J_SERVER.job_exists(test_name)):
            J_SERVER.delete_job(test_name)

         J_SERVER.create_job(test_name, xml_str)
         print("Generator added: ", test_name)
      except Exception as e:
         print("Generator fail - skipping", test_name, e)
         continue

   

if __name__ == "__main__":
   main()

