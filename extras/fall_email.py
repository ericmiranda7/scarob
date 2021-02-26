import smtplib, ssl

sender_email = "scarobbot50@gmail.com"
receiver_email = "ericmiranda7@gmail.com"
message = """\
Subject: Scarob Report

Your relative has fallen !"""

port = 465
password = 'thisissecure1!'

context = ssl.create_default_context()

with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
    server.login("scarobbot50@gmail.com", password)
    server.sendmail(sender_email, receiver_email, message)