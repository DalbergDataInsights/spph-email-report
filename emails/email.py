from email.MIMEMultipart import MIMEMultipart

class Email:



    def __init__(self, smtp, send_to, send_from):
        self.smtp = smtp
        self.send_to = send_to
        self.send_from = send_from
        self.message = 