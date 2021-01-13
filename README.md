# SPPH-EMAIL-REPORT  


The main aim of the current program is to create the given number of emails with the customized set of visualisations of indicators presented in the CEHS tool.  

The current instruction file will serve as a step-by-step guide, which shows how to run the program and gives the information on its structure and underlying scripts.  

Shortly, the program consists of two parts:  
  
* Creation of the visualisations and captions
* Creation of the emails

Consequently, it is impossible to successfully execute the second part until the first part is completed. 
The output of the first part of the program is a json file and for visualisations for each indicator. First three visualisations are a scatter plot with district-level overview of the indicator, a bar chart with facilities' contribution and reporting scatter plot. The fourth visualisation is a country-level overview scatter of the indicator. The json file contains titles of the figures, which are implemented to emails as figures' captions.  
Output of the second part of the program is emails.

The content of the instruction file is structured as follows:  

## CONTENT

1. [How to run the program](#first)
2. [How to change recipients](#second)
3. [How to change a sender](#thirdnull)
4. [How to choose a reporting date](#third)
5. [How to add or delete indicators or districts](#fourth)
6. [How to alter an email template](#fifth)
    1. [Adding figures](#fifthpointone)
    2. [Adding captions](#fifthpointtwo)
7. [How to alter captions](#sixth) 
8. [Dictionary for developers](#seventh)


### HOW TO RUN THE PROGRAM <a name="first"></a>

The script [app.py](app.py) is the script which runs the program.  
In order to start running it is necessary to scroll down the script until  
```python
if __name__ == "__main__":
    run(["extract"])
```

`run([])` in the body of the function allows to choose the operation, which must be performed. The name of operations are given as pipes in `def run(pipeline)` above:  
  
1. "extract" - creates and prints the visualisations to the predefined folders;
2. "email_save" - compiles and saves the emails using the given set of indicators and districts;
3. "email_send" - sends already created emails off  
4. "email_to_pdf" - converts .msg files (emails) into pdf  
5. "increment-date" - upgrades the date to the current month (doesn't change anything if already upgraded)

NB! Check the date of the report before starting the extraction (see:[How to choose a reporting date](#third))
To change predefined input, use configuration files in a config folder in the workspace.  

This section is under the development, so the changes will be implemented soon.  

### HOW TO CHANGE RECIPIENTS <a name="second"></a>

In config folder open [email_recipients.json](config/email_recipients.json)
config >> email_recipients.json

Change or add and email address in "recipients". Note, that each dictionary {} refers to only one district. So, by adding the email address, the original email won't be changed.  
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

### HOW TO CHANGE A SENDER <a name="thirdnull"></a>

The sender's email credentials are set in the .env file (text configuration file) as the last three constants:  

```
export SMTP=smtp-mail.outlook.com
export USERNAME=name@outlook.com
export PASSWORD=xxxx
```

Use your account name and a password.  
Note! That if the new account is not outlook account, change the SMTP accordingly.  
Example: smtp-mail.outlook.com -> smtp.gmail.com for a gmail account.  


### HOW TO CHOOSE THE DATE <a name="third"></a>

To choose the date open [config.json](config/config.json).  

In dictionary in "date" change the date, keeping the preset format: YYYYMM -> 202011 is November 2020.
Note, this change affects the data extraction (data is extracted for the given month) and automatically updates the email, so that no altering of template is necessary for the new date.

### HOW TO ADD OR DELETE INDICATORS OR DISTRICTS <a name="fourth"></a>

The used indicators are listed in [config.json](config/config.json).  

Add or delete districts is possible in the "districts" list.
Add or delete indicators is possible in the "indicators" list. Note, that indicators must be named identically to the ones in the database in use.  

Note! In here only extraction of images and relevant transformation of data will be changed. Altering the indicators/districts at this point won't change the emails. To implement related changes to the emails, please see the section [How to alter an email template](#fifth).  

### HOW TO ALTER THE EMAIL TEMPLATE <a name="fifth"></a>

To see the template in config folder open [email_template.json](config/email_template.json).  

All the text information can be altered directly there, keeping the preset format. For more information see any [HTML Style Guide and Coding Conventions](https://www.w3schools.com/html/html5_syntax.asp).
The pdf file, which shows links between mail_template.json and created email for Amuru district is [here]  

#### ADDING FIGURES <a name="fifthpointone"></a>

In the template figures are defined in a following form:

```python  
"<div>%image.1st ANC Visits.figure_1%<div/>",
```

while adding the picture, replicate the syntax: `<div>%image.*indicator's name*.*figure number*%<div/>`, where indicator's name is defined similarly to the one in config.json.  
The figures numbers can be found in data/viz in relevant folders.  
If there is a mistake in the parameters the code comes up with an error message and stops execution.  
#### ADDING CAPTIONS <a name="fifthpointtwo"></a>

In the template captions are defined in a following form:

```python
"<p style=\"color:rgb(42, 87, 131); \"><i>%title.1st ANC Visits.figure_1% </i></p>",
```

while adding the picture, replicate the syntax: `%title.*indicator's name*.*figure number*%`, where indicator's name is defined similarly to the one in config.json and figure's number corresponds to the related to the caption figure. To read the caption before adding, open titles.json in [data/viz/**date**/**district**/**indicator**](data/viz).  

### HOW TO ALTER CAPTIONS <a name="sixth"></a>

To change the captions, open figures' pipeline -> [figures/pipeline.py](figures/pipeline.py) and make necessary changes in `"titles"`. Note that districts' level pipeline is `pipeline`, the `national_pipeline` is for country-level monthly reports.  

To add more arguments to the caption, add name of the argument to the `"title_args":`, place it to the `"titles"` as `{}` and define a new argument in extract/model/figure_factory.py in  

```python
def get_figure_title(self, title, db, aggs):
    format_aggs = []
        indicator = next(iter(db.datasets.values())).columns[-1]
        for agg in aggs:
            parsed = ""
            if agg == "date":
                data = db.datasets.get("district_dated")
                parsed = data.reset_index().date.max().strftime("%B %Y")
            ...
            elif agg == "reference_date":
                data = db.datasets.get("country")
                data_today = data.reset_index().date.max()
                parsed = (data_today - relativedelta(years=1)).strftime("%B %Y")
            format_aggs.append(parsed)
        return title.format(*format_aggs)   
```

Where the new argument is to define after the if-statement.  
### FOR DEVELOPERS <a name="seventh"></a>

#### Table of content of the program  

* [config](#config) - configuration files (.json)
* [data](#data) - output folder, where visualisations and captions (in json format) are stored
* [dataset](#dataset) - data transformation
* [emails](#emails) - creation and compilation emails
* [extract](#extract) - creation of visualisations and captions
* [figures](#figures) - figures' pipeline  
* [app](#first) - script, which runs the program

##### CONFIG <a name="config"></a>
The folder contains currently four config files (.json).  
[config_national.json](config/config_national.json) is the config file, which interacts with the [national pipeline](figures/pipeline.py) and serves for monthly report needs. Output: country-level visualisations.  
[config.json](config/config.json) contains the essential information for the district-level emails, incl. list of districts, date and list of indicators (for more see [here](#fourth))
[email_recipients.json](config/email_recipients.json) contains a list of dictionaries, where recipients' email addresses, names and districts are specified. Any changes in this json affect only dispatch of emails, but not visualisations or list of districts (for more, see [here](#second))  
[email_template.json](config/email_template.json) is the template in html-format. Brings together visualisations, captions and aggs (see [emails](#emails) and [How to alter an email template](#fifth) for more)

##### DATA <a name="data"></a>
Output directory.  
The folder [viz](data/viz) includes [extracted](#extract) visualisations and captions, sorted by district -> reporting date -> indicator.
The folder [emails](data/emails) keeps compiled emails as .msg  
The folder [pdf] contains pdf-files converted from .msg files. For details see [emails](#emails) in documentation and `class Email:` in the [module](emails/model.py) directly

##### DATASET <a name="dataset"></a>
The folder "dataset" contains helper, pipeline and transform.  
[Helper](dataset/helper.py) contains sorting by district and date functions.  
[pipeline.py](dataset/pipeline.py) contains functions, which fetch and clean raw data from the database for each type of visualisation. 
[transform](dataset/transform.py) contains functions, which structure the clean data in a form, suitable for visualisation. Here the data can be rearranged in case of unreadable representation or checked for errors if they are visible in a visualisation. 
Note! Errors in visualisations can origin from [figure factory](extract/model/figure_factory.py).  
##### EMAILS <a name="emails"></a>

The folder "emails" includes [model.py](emails/model.py) module. 
The module contains two main classes `class EmailTemplateParser` and `class Email`.  
`class EmailTemplateParser` includes functions, which compile the emails such as: `def get_parsed_message(self, filters)`, `def set_payload(self, message)` and `def get_parsed_subject(self, filters)`. Additionally, the class includes the parsers. These parsers define which information is inserted in the email template for automatically adaptable parts.  

The main parser:  

```python
def parse_item(self, item, filters):
        if "%date%" in item:
            item = self.__parse_date(item, filters)
        elif "%image" in item:
            item = self.__parse_image(item, filters)
        elif "%district%" in item:
            item = self.__parse_district(item, filters)
        elif "%title" in item:
            item = self.__parse_image_title(item, filters)
        elif "%recipients_name%" in item:
            item = self.__parse_recipients_name(item, filters)
        else:
            item = item
        return item
```

Example of parsing of a district:

```python
def __parse_district(self, item, filters):
        item = item.replace("%district%", filters.get("district"))
        return item
```

Note! Sometimes there is a chained .replace() in the body of a parser. It is made due to necessity to keep automatic parts in one string in the template. The only way to do several different replacements in one string is the chained replace. See an example below.  

```python
def __parse_date(self, item, filters):

        date = self.config.get("date")
        year = date[:4]
        month = date[-2:]
        month = calendar.month_name[int(month)]
        date = f"{month} {year}"

        item = item.replace("%district%", filters.get("district")).replace("%date%", date)

        return item
```

In the above example: the subject of the emails contain two adaptable parts - district's name and the date. So the doubled `.replace()` is used.  
Note: there are also secondary functions in [init](emails/__init__.py).  

##### EXTRACT <a name="extract"></a>

The backbone of the visualisations' printing is based in the [extract](extract) folder.  
The path where figures and their titles (=captions) are being stored, defined in [init.py](extract/__init__.py).  
The extract contains figure and model folders.  

[Figure](extract/figure) defines in [_init.py_](extract/figure/__init__.py) the following feature: images with title are being skipped without interrupting code execution if relevant data is missing. Instead in email the error message will be parsed. The error message is defined in emails/model.py in  `def __parse_image(self, item, filters, mime_type=True)`.  
[Model](extract/model) contains [database](extract/model/database.py), which contains settings for data fetching and allows to filter the data by policy in `class Database`.  
Policy options:  

* Correct outliers - using standard deviation: std,
* Correct outliers - using interquartile range: iqr,
* Keep outliers: out.
By default "out" is chosen for the SPPH emails.  

[Figure factory](extract/model/figure_factory.py) contains functions for visualisations building with the plotly graphing library. Both types of visualisations (scatters and a bar chart) is being developed with the one function `def get_bar_or_scatter`. Important is the definition of varying parts of figures' titles, which is done via  

```python
def get_figure_title(self, title, db, aggs):
  
        format_aggs = []
        indicator = next(iter(db.datasets.values())).columns[-1]
        for agg in aggs:
            parsed = ""
            if agg == "date":
                data = db.datasets.get("district_dated")
                parsed = data.reset_index().date.max().strftime("%B %Y")
            ....
            elif agg == "district":
                data = db.datasets.get("district_dated")
                parsed = data.reset_index().id[0]

            elif agg == "indicator_view":
                parsed = db.get_indicator_view(indicator)
            ...
        return title.format(*format_aggs)        

```

where each agg is one of the title_aggs from the figures/pipeline.py (see [figures](#figures) for more).  

##### FIGURES <a name="figures"></a>

pipeline.py in figures contains pipeline for emails and national pipeline for monthly reports.  
The pipeline for emails is in the scope of interest. For example,  

```python
{
        "type": "scatter",
        "transform": scatter_district_plot,
        "color": {
            2018: "rgb(185, 221, 241)",
            2019: "rgb(106, 155, 195)",
            2020: "rgb(200, 19, 60)",
        },
        "title": "The total {} in {} in {} <b>{}</b> from the month before",
        "title_args": ["indicator_view", "district", "date", "ratio"],
    }
```

from the pipeline defines the first figure (scatter plot with the indicator's overview) and its captions in `"title"`, while the  `"title_args"` accommodate all the adaptable parts of the captions. Titles can be change manually here, the relevant arguments take place of {} in the `"title"` and must be defined in order of appearance in `"title_args"` with the predefined names (see more in [extract](#extract)).  
 