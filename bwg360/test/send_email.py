#!/usr/bin/python
# -*- coding: utf-8 -*-

import time


def send_email(user, pwd, recipient, subject, body):
    import smtplib

    FROM = user
    TO = recipient if isinstance(recipient, list) else [recipient]
    SUBJECT = subject
    TEXT = body

    # Prepare actual message
    message = """From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    try:
        start = time.time()
        print('try to send email')
        server = smtplib.SMTP("smtp.gmail.com", 587)
        print('create email server[%d]', time.time()-start)
        server.ehlo()
        print('server ehlo[%d]', time.time()-start)
        server.starttls()
        print('server start tls[%d]', time.time()-start)
        server.login(user, pwd)
        print('server login[%d]', time.time()-start)
        server.sendmail(FROM, TO, message)
        server.close()
        print('successfully sent the mail[%d]', time.time()-start)
    except Exception as e:
        print("failed to send mail, ", e)


if __name__ == '__main__':
    send_email('*******', '*******', '*********', 'hello', 'testing...')