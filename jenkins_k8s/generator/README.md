# Job generator
Script creates Jenkins jobs from templates configurations.
Tool creates job for each test in the target Jenkins instance.

# Templates
* pipeline_tamplate_cfg - Simple declarative pipeline

# Environment requirements
* JENKINS_ID=<username>
* JENKINS_TOKEN=<user access token>
* JENKINS_URL=<jenkins url>

# Run example
`
JENKINS_ID=MyUser JENKINS_TOKEN=**** JENKINS_URL=pipeline.scribesecurity.com:8080 python3 create_jobs.py
`

# Repo dir hierarchy
* <test_group> - Currently supporting <`jekins_k8s`>
    * <test_name> - Name must include `test`
        * Jenkinsfile   

# JOb hierarchy
Test creates a folder and jobs in the fallowing format.
* <repo_name>/<test_group>/<test_name>
