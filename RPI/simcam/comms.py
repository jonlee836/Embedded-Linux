#! /usr/bin/python2
import os
import json
import email
import mailbox
import smtplib
import imaplib
import datetime

from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate

def send_msg(txtmsg, imgpath = None):

    json_dir = os.path.expanduser('~/gitstorage/confs/sendmail.json')
    with open(json_dir) as data_file:
        conf = json.load(data_file)
        
    TEXT = txtmsg
    username = conf["USER_NAME"]
    password = conf["USER_PASS"]
    from_addr = conf["FROM_ADDR"]
    to_addr = conf["TO_ADDR"]
    
    msg = MIMEMultipart()
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = conf["SUBJECT"]
    
    bodymsg = MIMEText(TEXT, 'plain', 'us-ascii')
    msg.attach(bodymsg)

    if imgpath is not None:
        img_data = open(imgpath, 'rb').read()
        image = MIMEImage(img_data, name=os.path.basename(imgpath))
        msg.attach(image)
    
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(username,password)
    server.sendmail(from_addr, to_addr, msg.as_string())
    server.quit()
    
def get_msg():

    currtime = datetime.datetime.now()
    json_dir = os.path.expanduser('~/gitstorage/confs/sendmail.json')

    with open(json_dir) as data_file:
        conf = json.load(data_file)

    text_msg = ""
    username = conf["USER_NAME"]
    password = conf["USER_PASS"]

    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login(username, password)
    mail.list()
    mail.select('inbox')
    result, data = mail.uid('search', None, "UNSEEN")
    i = len(data[0].split())
    
    for x in range(i):

        latest_email_uid = data[0].split()[x]
        result, email_data = mail.uid('fetch', latest_email_uid, '(RFC822)')
        raw_email = email_data[0][1]
        raw_email_string = raw_email.decode('utf-8')
        email_message = email.message_from_string(raw_email_string)

        #write something that will make it
        #only care about emails +- 10 seconds on the same date, hour, minute
        
        for part in email_message.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True)

                if body == "ALARM ON":
                    return "ON"
                elif body == "ALARM OFF":
                    return "OFF"
                
