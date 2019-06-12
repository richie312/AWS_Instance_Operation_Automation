# AWS_Instance_Operation_Automation
AWS operation automation with Python and notification with daily mail on usage and cost of AWS instances.
Firstly it checks the usage of alal the instances and if the usage exceeds the threshold value of 95%, it switch of that particular instance and log the report. 
It also sends the daily email to the user about the usage and the api cost. The script is hosted on aws and cronjob is setup for the task.
