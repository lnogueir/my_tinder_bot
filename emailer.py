from EmailAccount import Account
import smtplib
from smtplib import *
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from helpers import handle_girl_photos
import os, shutil



class Emailer:
	connected=False
	connection=None
	def __init__(self):
		self.emailer=Account()
		self.content=None

	def connect(self):
		if not Emailer.connected:
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
				Emailer.connected=True
				Emailer.connection = connection

	@classmethod
	def disconnect(cls):
		if cls.connected:
			cls.connection.close()
			cls.connected=False

	def make_email(self,girl,kind):
		try:
			if not Emailer.connected:
				self.connect()
			msg = MIMEMultipart()
			msg["From"] = self.emailer.user
			msg["To"] = self.emailer.receiver
			msg["Subject"] = "Congratulations Master Lucas! You've got a new " + kind + "."
			body = "Girl's information:\n"
			body+= "Name: " + girl['name'] + "\n"
			body+= "Age: " + str(girl['age']) + "\n"
			body+= "Bio: " + girl['bio'] + "\n"
			body+= "And most importantly, her photos are attached to this email.\n"
			if kind == 'match':
				body+= "Don't forget to submit your intentions to me.\n\n"
			elif kind =='date':
				body+= "Good Luck talking to the woman, you might need it.\n\n"
			body+= "Sincerily,\n"
			body+= "Your Bot."
			msg.attach(MIMEText(body,'plain'))
			photos_file = handle_girl_photos(girl['photos'])
			attachment = open(photos_file,'rb')
			part = MIMEBase('application','octet-stream')
			part.set_payload((attachment).read())
			encoders.encode_base64(part)
			part.add_header('Content-Disposition',"attachment; filename= "+photos_file)
			msg.attach(part)
			self.content = msg.as_string()
			if os.path.isdir("tmpdir"):
				shutil.rmtree("tmpdir")
		except:
			self.disconnect()		


	def make_alert_email(self):
		try:
			if not Emailer.connected:
				self.connect()
			msg = MIMEMultipart()
			msg["From"] = self.emailer.user
			msg["To"] = self.emailer.receiver
			msg["Subject"] = "Master Lucas, its time to authenticate!"
			body = "Please check if your server is on in so we can send you an SMS with your new token.\n"
			body+= "If it is, please enter the code on your terminal.\n"
			body+= "Sincerily,\n"
			body+= "Your Bot."
			msg.attach(MIMEText(body,'plain'))
			self.content = msg.as_string()
		except:
			self.disconnect()	


	def send_email(self):
		if Emailer.connected:    
			try:
				Emailer.connection.sendmail(self.emailer.user,self.emailer.receiver,self.content)
			except SMTPRecipientsRefused as e:
				refused = e.recipients
				print("ERROR: "+str(e.recipients))
			else:
				print("EMAIL SENT SUCCESSFULLY")
				if os.path.exists('girl_photos.zip'):
					os.remove('girl_photos.zip')	        






	    
