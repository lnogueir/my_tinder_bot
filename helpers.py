import requests
import shutil
import os
from datetime import datetime
from automatic_messages import AUTOMATIC_MESSAGES

def handle_girl_photos(photos): #Make a zip file of the girl's images
	if os.path.isdir("tmpdir"):
		shutil.rmtree("tmpdir")
	os.mkdir("tmpdir")
	for i,image_url in enumerate(photos):
		f = open('tmpdir/'+str(i)+'.jpg','wb')		
		try:
			f.write(requests.get(image_url).content)
		except:
			print("ERROR DOWNLOADING IMAGES")	
		f.close()
	shutil.make_archive('girl_photos','zip','tmpdir') 
	return 'girl_photos.zip'

def get_girls_age(today,girl_bd):
	clean_birth_date = girl_bd[:-5] + 'Z' 
	birth_date_obj = datetime.strptime(clean_birth_date, '%Y-%m-%dT%H:%M:%SZ')
	age_obj = today - birth_date_obj
	return int(age_obj.days/365)


def create_message(girl_name, kind):
	message = ''
	if kind == 'slut' or kind == 'nerd':
		message += "Hello " + girl_name + "!!"
	elif kind == 'invalid_reply':
		message += "Sorry " + girl_name
	message += AUTOMATIC_MESSAGES[kind]
	return message



#### FIXED 
#JUST CHECK IF ANY OF THE MESSAGES WERE THE PRE MADE ONES
def get_her_messages(girl_name, new_messages):
	return [message.rstrip('\n\r') for message in new_messages if (create_message(girl_name,'slut').rstrip('\n\r')!=message.rstrip('\n\r') and message.rstrip('\n\r') != create_message(girl_name,'nerd').rstrip('\n\r') and create_message('Eda','invalid_reply').rstrip('\n\r')!=message.rstrip('\n\r') and message.rstrip('\n\r') != AUTOMATIC_MESSAGES['YES DADDY'].rstrip('\n\r') and message.rstrip('\n\r') != AUTOMATIC_MESSAGES['more'].rstrip('\n\r'))]


def get_my_messages(girl_name, new_messages):
	return [message.rstrip('\n\r') for message in new_messages if not (create_message(girl_name,'slut').rstrip('\n\r')!=message.rstrip('\n\r') and message.rstrip('\n\r') != create_message(girl_name,'nerd').rstrip('\n\r') and create_message('Eda','invalid_reply').rstrip('\n\r')!=message.rstrip('\n\r') and message.rstrip('\n\r') != AUTOMATIC_MESSAGES['YES DADDY'].rstrip('\n\r') and message.rstrip('\n\r') != AUTOMATIC_MESSAGES['more'].rstrip('\n\r'))]

# Test message
# all_messages = ['Hello Eda!! This is an automated message to remind you of your upcoming "Netflix and chill" appointment in the next week. To confirm your appointment text YES DADDY. To unsubscribe text WRONG HOLE.For more information type MORE. (Yes, it is case sensitive lool)\n', 'YES DADDY', 'Thank you for choosing us.\nLucas will reach you shortly.', 'Skskskjdhf', 'Wtf', '😂😂😂😂', "Sorry Eda, unrecognized message.\nPlease confirm with 'YES DADDY'.\nTo unsubscribe, text 'WRONG HOLE'.", "Sorry Eda, unrecognized message.\nPlease confirm with 'YES DADDY'.\nTo unsubscribe, text 'WRONG HOLE'.", "Sorry Eda, unrecognized message.\nPlease confirm with 'YES DADDY'.\nTo unsubscribe, text 'WRONG HOLE'.", 'Damn it bot, those last three messages werent supposed to be sent lool', 'So i see youve confirmed our session.', 'Is this correct Eda? 😅']




