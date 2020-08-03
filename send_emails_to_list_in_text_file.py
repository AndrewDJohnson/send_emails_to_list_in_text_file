""" Python Bulk Emailer - NOT FOR SPAMMING!
    I wrote this to send important information to about 20,000 addresses - as a way of combating mainstream propaganda.
    Designed to be run as a cronjob or similar...
    1) Reads an HTML email from a file
    2) Reads email addresses from a file
    3) Sends message - (with an attachment) requesting read receipt - to each of the email addresses
    4) Moves the file of addresses to a sub folder
 
    The idea is that it can be run as CRON job, say every 30 mins, to send about 50 or 100 emails from your ISP address.
    There are problems using this from a microsoft or Gmail address because of Spam limitations (about 100 messages per day allowed or something)
    
    There is a list in the code below in which you can put your email account details - SMTP server, username and password.
    You may need to use SSL or TLS email sending, depending on your server.
    You may need to logon to your email account and set the "allow less secure apps to connect" flag, or generate a custom password (needed for GMail accounts)
    
    Cobbled together by Andrew Johnson, June/July 2020
    
    If you have a text file with ALL your email addresses in, one per line, in Linux, you can split the file up into, say, blocks of 50 emails thus:
    
        split -l 50 -d all_emails_addrs.txt email_addrs_block 
    
    and this will create a set of numbered files, each with 50 lines.
    
    Run this python program as a CRON job - say every 30 mins - and it will send batches of mails every 30 mins
    
"""    
#Import libraries for the various features we need!
import os, sys
import glob
import traceback
import logging
import smtplib
import ssl
from pathlib import Path
import codecs
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.utils import COMMASPACE, formatdate
from email import encoders

#Function to send an email by SSL, which some servers use.
def send_ssl_email(server,user, pwd, message):
    message['From'] = '"Andrew Johnson" <' + user + '>'
    #This line adds in the "read receipt" request.
    message['Disposition-Notification-To'] = user
    message['Reply-To'] = user    
    print ("Loading SMTP library")
    smtpserver = smtplib.SMTP_SSL(server)
    print ("Connecting SSL to ", server)
    try:
        smtpserver.login(user, pwd)
        smtpserver.sendmail(user, msg["To"].split(","), message.as_string())
        smtpserver.close()
        print('Sent') 
        return True
    except Exception as e:
        print (traceback.format_exc())
        #logging.error(traceback.format_exc())
        return False

#Function to send an email by TLS, which some servers use. 
def send_tls_email(server,user, pwd, message):
    message['From'] = '"Andrew Johnson" <' + user + '>'
    #This line adds in the "read receipt" request.
    message['Disposition-Notification-To'] = user
    message['Reply-To'] = user
    try:
        print ("Connecting to ",server)
        server = smtplib.SMTP(server, 587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(user, pwd)
        print ("Logged in")
        server.sendmail(user, msg["To"].split(",") , message.as_string())
        #server.sendmail(user, to, "Test message")
        server.close()
        print ('Successfully sent the mail')
        return True
    except Exception as e:
        print (traceback.format_exc())
        #logging.error(traceback.format_exc())
        return False

#Now we set up the email message itself 
msg = MIMEMultipart("Test")
msg['Subject'] = 'Subject'

#Write the plain text part if you want - not essential, as these days, most clients can read HTML.
text = """Please open in a client which can read HTML emails."""
#We have to open the HTML file in the right way.
#It would be best to keep the HTML relatively simple - perhaps you can save it out from your email client.
f=codecs.open("email_to_send.htm", 'r','utf-8')
html=f.read()
#Convert to MIME format
part2 = MIMEText(html, "html")
part1 = MIMEText(text, "text")
#Attach the mime elements to the message.
msg.attach(part2)
msg.attach(part1)

#Now attach any files you want to send - set up the file name at the line below or use a wildcard etc
files=["files.*"]
files=["THE-COVID-19-Pandemic-Challenging-the-Narrative.pdf"]
for path in files:
    part = MIMEBase('application', "octet-stream")
    with open(path, 'rb') as file:
        part.set_payload(file.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition',
                    'attachment; filename="{}"'.format(Path(path).name))
    msg.attach(part)

#You can use different email accounts to send your bulk messages - perhaps sending 50 from each account every 30 mins or something.
email_accounts=[["smtp.isp1.com","--- email 1----", "password 1"],
                ["smtp.isp2.com","--- email 2----", "password 2"],
                ["smtp.isp3.com","--- email 3----", "password 3"]    ]
#Count how many email addresses were defined.
batch_size=len(email_accounts)

#The email addresses should be one per line 
#Get a recursive list of file paths that matches pattern including sub directories
fileList = glob.glob('email_addresses*', recursive=False)
#Sort the list into alphabetical order.
fileList.sort() 
no_files=len(fileList) 

print (datetime.datetime.now().strftime("%Y-%m-%d %H:%M")," - ",no_files," blocks of emails left to send!")

#We will try to do a batch, but maybe we got to the end of the files, so we will have a smaller batch.
if no_files>batch_size:
    no_files=batch_size
recipient_list=[]
#On each run, we will read one file of email addresses to be sent using one of the email accounts defined above.
for i in range (0, no_files):
   file=fileList[i]
   print (file)
   with open(file, 'r') as file_obj:
        file_data = file_obj.readlines()
   #Reset recipient list to empty
   
   recipient_list=""
   for line_text in file_data:
       recipient_list=recipient_list + line_text.strip()+ ','
   
   #By default, these fields may be  generated when the message is created in the code above.
   #We want to modify these fields so we will add them again later.
   del msg['To']
   del msg['From']
   del msg['Reply-To']
   del msg['Disposition-Notification-To']
   
   #Set the recipient to the list of addresses we read in.
   msg['To'] = recipient_list
   print (recipient_list)
   #SSL mail seems to be the most common... 
   email_status=send_ssl_email(email_accounts[i][0],email_accounts[i][1],email_accounts[i][2],msg)
   #but you might need to send TLS mail instread....
   #email_status=send_tls_email(email_accounts[i][0],email_accounts[i][1],email_accounts[i][2],msg)

   #If mail was sent OK, we move the file of addresses to the "done" folder,so it picks up the next one on the next run
   if email_status==True:
       os.rename (file,"done/"+file)


