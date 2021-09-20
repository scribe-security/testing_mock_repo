import os
import jenkins
import xml.etree.ElementTree as ET
from git import Repo
from pathlib import Path

# def convert_xml_file_to_str(path_to_config_file):
#     tree = ET.parse(path_to_config_file)
#     definition = tree.find('definition')
#     script_path = definition.find("scriptPath")
#     script_path.text = "testing123"
#     return ET.tostring(root, encoding='utf8', method='xml').decode()

def read_xml(path_to_config_file):
    tree = ET.parse(path_to_config_file)
    return tree

def xml_modify(tree, jenkins_path):
    definition = tree.find('definition')
    script_path = definition.find("scriptPath")
    script_path.text = jenkins_path

def xml_toStr(tree):
    root = tree.getroot()
    return ET.tostring(root, encoding='utf8', method='xml').decode()

def read_jobs(J_SERVER):
   jobs = J_SERVER.get_jobs()
   for job in jobs:
      job_name = job['name']
      job_config = J_SERVER.get_job_config(job_name)
      job_dir = "jobs"
      if not os.path.exists(job_dir):
         os.mkdir(job_dir)
      job_file = open(job_dir + '/' + job_name + '.xml', 'w')
      job_file.write(job_config)
      job_file.close()

def main():
   J_ID = os.environ['JENKINS_ID']
   J_TOKEN = os.environ['JENKINS_TOKEN']
   J_ADDR = os.environ['JENKINS_URL']
   J_URL = 'http://%s:%s@%s' % (J_ID, J_TOKEN, J_ADDR)
   J_SERVER =  jenkins.Jenkins(J_URL)

   repo = Repo(search_parent_directories=True)
   repo_name = repo.remotes.origin.url.split('.git')[0].split('/')[-1]
   base_testdir = Path(repo.git_dir).parent
   
   test_type = "jenkins_k8s"
   test_template = "fixtures/pipeline_template_cfg.xml"
   test_dir = ".."
   test_dirs = Path(test_dir).glob("*test*")

   for dir in test_dirs:
      try:
         folder_name = repo_name
         sub_folder_name = os.path.join(folder_name, test_type)
         test_name = '%s/%s' % (sub_folder_name, dir.stem)
         xml_tree = read_xml(test_template)
         jenkins_path = '%s/Jenkinsfile' % (dir.stem)
         jenkins_path = os.path.join(test_type, dir.stem, "Jenkinsfile")
         xml_modify(xml_tree, jenkins_path)
         xml_str =  xml_toStr(xml_tree)
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

