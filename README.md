# send_emails_to_list_in_text_file
Python Bulk Emailer - NOT FOR SPAMMING!
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
