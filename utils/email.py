# in this example, this handles email sending functionality in order to report alerts.
import smtplib
import csv
import io
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from typing import Dict
from dataclasses import dataclass, field

@dataclass
class EmailData: 
    text: str = ""
    from_email: str = ""
    to_email: str = ""
    subject: str = ""
    # if is csv
    is_csv: bool = False
    csv_headers: list[str] = field(default_factory=list)
    csv_rows: list[str] = field(default_factory=list)
    # Connector
    server: str = ""
    port: int = 0
    username: str = ""
    password: str = ""

class EmailHandler:
    def __init__(self, emaildata: EmailData):
        self.emaildata = emaildata

    def send_email(self) -> Dict:
        msg = MIMEMultipart()
        msg['Subject'] = self.emaildata.subject
        msg['From'] = self.emaildata.from_email 
        
        if self.emaildata.is_csv:
            rows = [row for row in self.emaildata.csv_rows]
            # create in memory csv file
            csv_content = io.StringIO()
            csv_writer = csv.writer(csv_content)
            csv_writer.writerows(rows)
            
            # Attach csv file
            attachment = MIMEApplication(csv_content.getvalue())
            attachment.add_header('Content-Disposition', 'attachment', filename='report.csv')
            msg.attach(attachment)
            
        # Add text message to the email
        text_message = MIMEText(self.emaildata.text)
        msg.attach(text_message)

        # Connect to SMTP server
        try:
            with smtplib.SMTP(self.emaildata.server, self.emaildata.port) as server:
                server.starttls()
                server.login(self.emaildata.username, self.emaildata.password)
                server.sendmail(self.emaildata.from_email, self.emaildata.to_email, msg.as_string())
            return {"success":True, "msg":f"Email sent from {self.emaildata.from_email} to {self.emaildata.to_email}"}
       
        except Exception as error:
            return {"success":False, "msg":error}
        
