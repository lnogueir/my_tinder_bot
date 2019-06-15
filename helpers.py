import requests
import shutil
import os
from automatic_messages import AUTOMATIC_MESSAGES

def handle_girl_photos(photos): #Make a zip file from the selected items by the user
	if os.path.isdir("tmpdir"):
		shutil.rmtree("tmpdir")
	os.mkdir("tmpdir")
	for i,photo in enumerate(photos):
		f = open('tmpdir/'+str(i)+'.jpg','wb')
		try:
			f.write(requests.get(photo).content)
		except:
			print("ERROR DOWNLOADING IMAGES")	
		f.close()
	shutil.make_archive('girl_photos','zip','tmpdir') 
	return 'girl_photos.zip'

def get_girls_age(today,girl_bd):
	clean_birth_date = girl_bd[:-5] + 'Z' 
	age_obj = today - clean_birth_date
	return int(age_obj.days/365)


def create_message(girl_name, kind):
	message = ''
	if kind == 'slut' or kind == 'nerd':
		message += "Hello " + girl_info["name"] + "!!"
        elif kind == 'invalid_reply':
		message += "Sorry " + girl_name
	message += AUTOMATIC_MESSAGES[kind]
	return message



