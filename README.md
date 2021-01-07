# SPPH-EMAIL-REPORT 


The main aim of the current programm is to create the given number of emails with the customized set of visualisations of indicators presented in the CEHS tool. 

The current instruction file will serve as a step-by-step guide, which shows how to run the program and gives the information on its structure and underlying scripts. 

Shortly, the program consists of two parts: 
* Creation of the visualusations and captions
* Creation of the emails
Consequently, it is impossible to successfuly execute the second part until the first part is completed. 
 

The content of the instruction file is structured as follows: 
1. HOW TO RUN THE PROGRAM 
2. HOW TO CHANGE RECEPIENTS
3. HOW TO CHOOSE THE REPORTING DATE 
4. HOW TO ADD OR DELETE INDICATORS OR DISTRICTS
5. HOW TO ALTER THE EMAIL TEMPLATE 
    4.1 ADD FIGURES
    4.2 ADD CAPTIONS UNDER THE FIGURES IN THE TEMPLATE 

##### HOW TO RUN THE PROGRAM 

The script "app.py" is the script which runs the program. 
In order to start running it is necessary to scroll down the script until 
```python
if __name__ == "__main__":
    run(["extract"])
```

`run([])` in the body of the function allows to choose the operation, which must be performed. The name of operations are given as pipes in `def run(pipeline)` above: 
1. "extract" - creates and prints the visualisations to the predifined folders;
2. "email" - compiles and sends off the emails with the given set of indicators to the predefined recipients in the districts. 

NB! Check the date of the report before starting extraction (see: HOW TO CHOOSE THE DATE )
To change predifined input, use configuration files in a config folder in the workspace. 

This section is under the development, so the changes will be implemented soon. 

#####  HOW TO CHANGE RECEPIENTS  

In config folder open email_recipients.json
config >> email_recipients.json

Change or add and email addressin "recipients". Note, that each dictionary {} refers to only one district. So, by adding the email address, the original email won't be changed. 
If it is necessary to send the same email but with the different recipient name, you have to copy the structure of a dictionary and change the name of the recipient in filters. 
For example: 
```python
{
        "recipients": [
            "valeriya.cherepova@dalberg.com"
        ],
        "filters": {
            "district": "AMURU",
            "recipients_name": "Dr Odong Patrick Olwedo",
        }
```

+ add the new greeting and additional recipient, which won't be mentioned in the email 
```python
{
        "recipients": [
            "valeriya.cherepova@dalberg.com", "email@gmail.com" 
        ],
        "filters": {
            "district": "AMURU",
            "recipients_name": "Dr XXXXX,
        }
```

##### HOW TO CHOOSE THE DATE 

To choose the date open config.json
config >> config.json

In dictionary in "date" change the date, keeping the preset formt: YYYYMM -> 202011 is November 2020.
Note, this change affects the data extraction (data is extracted for the given month) and automatically updates the email, so that no altering of template is necessary for the new date.   

##### HOW TO ADD OR DELETE INDICATORS OR DISTRICTS 

The used indicators are listed in config.json
config >> config.json

Add or delete districts is possible in the "districts" list.
Add or delete indicators is possible in the "indicators" list. Note, that indicators must be named identically to the ones in the database in use. 

Note! In here only extraction of images and relevant transformation of data will be changed. Altering the indicators/districts at this point won't change the emails. To implement related changes to the emails, please see the section "HOW TO ALTER THE EMAIL TEMPLATE". 

##### HOW TO ALTER THE EMAIL TEMPLATE

To see the template in config folder open email_template.json.
config >> email_template.json

All the text information can be altered directly there, keeping the preset format (for more information see any HTML Style Guide and Coding Conventions. For example, https://www.w3schools.com/html/html5_syntax.asp)
###### ADD FIGURES



##### FOR DEVELOPERS

SPPH-EMAIL-REPORT 
Table of content of the program: 
* config - configuration files (.json)
* data - output folder, where visualisations and captions (in json format) are stored
* dataset - data transformation. Pretty identical to CEHS' one
* emails - skrpts to create and compile emails
* extract - creation of visualisations and captions
* figures - figures' pipeline 

Notes on **emails**: 

Notes on **extract**: 

Figures are configured to be skipped in case of missing data, so the code execution doesn't stop. Change it in extract/figure/__init__.py

Visualisations are configured in extract/model/figure_factory.py. Besides visualisations, the varying part of the captions is defined there in `def get_figure_title`. 



Notes on **figures**: 



Figure's pipeline is located in >figures/pipeline.py. To change the captions is possible via this pipline in titles. 
"national_pipeline" is for national level figures, mostly used in a monthly report, "pipeline" is a district-level pipeline. 

Extraction of the figures from 

Data transform is pretty similar to one used in CEHS


Change the outlier policy is possible in extract/model/database.py -> in class Database choose relevant active_repo

Figures are configured to be skipped in case of missing data. Change it in extract/figure/__init__.py





    