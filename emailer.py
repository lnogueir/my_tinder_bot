from EmailAccount import Account
import smtplib
from smtplib import *
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from models.graph import GraphModel
from helpers import handle_girl_photos
import os



class EmailSender:
	connected=False
	connection=None
	def __init__(self):
		self.emailer=Account()
		self.content=None

	def connect(self):
		if not EmailSender.connected:
			try:
				connection = smtplib.SMTP('smtp.gmail.com',587)
				connection.ehlo()
				connection.starttls()
				connection.login(self.emailer.user,self.emailer.password)
			except SMTPResponseException as e:
				error_code=e.smtp_code
				error_message=e.smtp_error
				print('ERROR CONNECTING:'+str(error_message))
			else:
				EmailSender.connected=True
				EmailSender.connection = connection

	@classmethod
	def disconnect(cls):
		if cls.connected:
			cls.connection.close()
			cls.connected=False

	def make_email(self,girl,kind):
		if not EmailSender.connected:
			self.connect()
		msg = MIMEMultipart()
		msg["From"] = self.emailer.user
		msg["To"] = self.emailer.receiver
		msg["Subject"] = "Congratulations Master Lucas! You've got a new " + kind + "."
		body = "Girl's information:\n"
		body+= "Name: " + girl['name'] + "\n"
		body+= "Age: " + girl['age'] + "\n"
		body+= "Bio: " + girl['bio'] + "\n"
		body+= "And most importantly, her photos are attached to this email.\n"
		if kind == 'match':
			body+= "Don't forget to submit your intentions to me.\n\n"
		elif kind =='date':
			body+= "Good Luck talking to the woman, you might need it.\n\n"
		body+= "Sincerily,\n"
		body+= "Your Bot."
		msg.attach(MIMEText(body,'plain'))
		photos_file = handle_girl_photos(girl)
		attachment = open(photos_file,'rb')
		part = MIMEBase('application','octet-stream')
		part.set_payload((attachment).read())
		encoders.encode_base64(part)
		part.add_header('Content-Disposition',"attachment; filename= "+photos_file)
		msg.attach(part)
		self.content = msg.as_string()
		if os.path.isdir("tmpdir"):
			shutil.rmtree("tmpdir")
		if os.path.exists(photos_file):
			os.remove(photos_file)	


	def send_email(self):
		if EmailSender.connected:    
			try:
				EmailSender.connection.sendmail(self.emailer.user,self.emailer.receiver,self.content)
			except SMTPRecipientsRefused as e:
				refused = e.recipients
				print("ERROR: "+str(e.recipients))
			else:
				print("EMAIL SENT SUCCESSFULLY")
				# os.remove('attachments.zip')	        






	    
