from . import data

import smtplib

import argparse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
import base64




parser = argparse.ArgumentParser()
parser.add_argument("-f", "--from", dest="sender", help="sender email address", default="xxx@dalberg.com")
parser.add_argument("-t", "--to", dest="recipient", help="recipient email address")
parser.add_argument("-s", "--subject", dest="subject", help="email subject", default= )#"{config.get('district')} district - 12 CEHS indicators")
parser.add_argument("-i", "--image", dest="image", help="image attachment", default=False)

args = parser.parse_args()
msg = MIMEMultipart('related')

msg['Subject'] = args.subject
msg['From'] = args.sender
msg['To'] = args.recipient

encoded = base64.b64encode(open("figure1.png", "rb").read()).decode() #without encoding mails with attach. can be considered as spam

#the body of the mail
html = """\
    <html>
    <head>
    <body>
        <h1>This email provides you Data Insights on Essential Health Services in Amuru</h1>
         <p style="color:rgb(42, 87, 131);">1. TRENDS UNTIL SEPTEMBER 2020 </p>
         <p style="color:red;" > 1.1. MNCH </p>
         <p style="color:orange;" > 1.1.1. Number of first ANC visits<br> 1.1.2. Number of fourth ANC visits 
         <br> 1.1.3. Number of facility births <br> 1.1.4. Number of low-weight births </p>
         <h2 style="color:rgb(42, 87, 131);" > TRENDS UNTIL SEPTEMBER 2020 </h2>
         <p>style="color:Orange;">1.1.1. Total number of women attending their first ANC visit in Amuru</p>
         <img src="cid:image1 align="center";base64,{encoded}"/>
    </body>
    </html>
    
"""
# the MIME types
msgHtml = MIMEText(html, 'html')

if args.image is not False:
    img = open(args.image, 'rb').read()
    msgImg = MIMEImage(img, 'png')
    msgImg.add_header('Content-ID', '<image1>')
    msgImg.add_header('Content-Disposition', 'inline', filename=args.image)

msg.attach(msgHtml)
msg.attach(msgImg)



server = smtplib.SMTP(' ', 587) # if 587 doesn't work then smtplib.SMTP_SSL(" ", 465)
server.starttls()
server.login(' mail', ' PASSWORD')

server.sendmail((args.sender, args.recipient, msg.as_string())
{}
server.quit()
