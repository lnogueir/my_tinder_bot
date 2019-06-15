
## My files ##
import config, tinder_api 
from emailer import EmailSender
from helpers import get_girls_age, create_message
from phone_auth_token import sendCode, getToken
##

from datetime import datetime
import os, csv, time
import json, requests

## NEW IDEA
# RODAR UM SERVIDOR NO MEU PC ENQUANTO O BOT FICA RODANDO NO PC VELHO, SE DER MATCH ELE DA UM REQUEST
# NO MEU SERVIDOR QUE VAI ABRIR TODAS AS FOTOS DESSE MATCH E MANDAR UM EMAIL E AO MESMO TEMPO VAI PEDIR
# UMA RESPOSTA MINHA, ESSA RESPOSTA VAI NO RESPONSE DIZENDO SIM OU NAO, PARA VER SE VOU QUERER MANDAR A
# MENSAGEM E QUE TIPO DE MENSAGEM QUE EU MANDO OU SE EU VOU QUERER DAR UNMATCH


class TinderBot:
	def __init__(self):
		self.statistics	= {'total_matches' : 0, 'swipes': 0, 'cur_matches': 0, 'match_rate' : 0}
		statistics_path = 'tinder_statistics.csv'
		if os.path.exists(statistics_path):
			with open(statistics_path, newline='') as csvfile:
				csv_data = csv.reader(csvfile, delimiter=' ', quotechar='|')
				for row in csv_data:
			 		self.statistics[row[0]] = row[1]
		self.account_token = config.tinder_token
		self.matches = {}
		self.last_like_at = None
		self.last_auth_at = None


	def isSwipeTime(self):
		if self.last_like_at:
			time_elapsed = (datetime.now() - self.last_like_at) # time as datetime object
			time_elapsed = timeElapsed.total_seconds()
			time_boundary = 43200 # 12 hours -- time to swipe again
			return (timeElapsed / time_boundary) > 1
		return True # First iteration

	def update_statistics_file(self):
		with open('tinder_statistics.csv', 'w', newline='') as csvfile:
		    writer = csv.writer(csvfile, delimiter=' ',quotechar='|', quoting=csv.QUOTE_MINIMAL)
		    for stat in self.statistics:
		    	writer.writerow([stat] + [self.statistics[stat]])
		    
	def isLucasOn(self):
		try:
			requests.get(config.aws_host)
		except:
			return False
		else:
			return True	    


	def swipe_right(self):
		try:
			LIKES_LIMIT = 85 #Tinder has a limit of 100 like per 12 hours, like 85 so we are safe.
			track_iterator = 0
			while track_iterator <= LIKES_LIMIT:
				recommendations = tinder_api.get_recommendations()['data']['results']
				for rec in recommendations:
					girl_id = rec['user']['_id']
					tinder_api.like(girl_id)
					self.statistics['swipes']+=1
					track_iterator+=1 
					if track_iterator == LIKES_LIMIT: # Check if its time to stop liking
						self.last_like_at = datetime.now()
						self.update_statistics_file()
						break
					time.sleep(10)	
		except:
			print('ERROR')



	def onMatch(self,match):
		self.statistics['total_matches']+=1
		self.statistics['match_rate'] = self.statistics['total_matches']/self.statistics['swipes']
		girl = match['person']
		self.matches[match['_id']] = {
			'name': girl['name'],
			'age': get_girls_age(datetime.now(), girl['birth_date']),
			'messages': {message_obj['message']:i for i,message_obj in enumerate(match['messages'])},
			'photos': [photo_obj['processedFiles'][0]['url'] for photo_obj in girl['photos']], # get url for each photo of the girl
			'bio': match['bio']
		}
		emailer = EmailSender()
		emailer.connect()
		emailer.make_email(girl,'match')
		emailer.send_email()
		emailer.disconnect()
		while not self.isLucasOn():
			time.sleep(10)
		try:
			url = config.aws_host + "/match"
			r = requests.post(url,headers={"content-type": "application/json"},data=girl)
			response = r.json()
		except Exception as e:
			print(e)	
			return {"error": "Something went wrong when trying to communicate with Lucas."}
		if bool(response["will_unmatch"]):
			match_id = match['_id']
			del self.matches[match_id]
			return tinder_api.unmatch(match_id)
		else:	
			self.matches[match['_id']].update({"girl_type" : response['girl_type']})
			self.matches[match['_id']].update({"send_automatic" : bool(response['send_automatic'])})
			return tinder_api.send_msg(match['_id'], response['message'])

	def onNewMessage(self, old_messages, new_messages, match_id):
		total_computed_messages = len(old_messages)
		valid_messages={}
		if 'WRONG HOLE' or 'WIERD' in new_messages:
			del self.matches[match_id]
			return tinder_api.unmatch(match_id)
		if 'YES DADDY' or 'LETS GO' in new_messages:
			valid_messages.update({'YES DADDY':old_messages['YES DADDY']})
		if 	'MORE' in new_messages:
			valid_messages.update({'MORE':old_messages['MORE']})
		if len(valid_messages) > 0: #There has been at least one valid message
			for m in sorted(valid_messages):
				if valid_messages[m] > total_computed_messages:
					if 'YES DADDY' == m: #New date!!
						tinder_api.send_msg(match_id,create_message(self.matches[match_id]['name'],"YES DADDY"))
						self.matches[match_id]['send_automatic'] = False
						emailer = EmailSender()
						emailer.connect()
						emailer.make_email(girl,'date')
						emailer.send_email()
						emailer.disconnect()
					else:
						tinder_api.send_msg(match_id,create_message(self.matches[match_id]['name'], "more"))		
					
				
		else:
			tinder_api.send_msg(match_id,create_message(self.matches[match_id]['name'],"invalid_reply"))			

	def update(self):
		matches = tinder_api.get_updates()['matches']
		self.statistics['cur_matches'] = len(matches)
		for match in matches:
			match_id = match['_id']
			if match_id not in self.matches: # new match !! 
				self.onMatch(match)
			else:
				new_messages = [message_obj['message'] for message_obj in match['messages']]
				old_messages = self.matches[match_id]['messages']
				if self.matches[match_id] and old_messages != new_messages: # new message!
					self.onNewMessage(old_messages,new_messages,match_id)

	def isAuthTime(self): # Every 24 hours we need a new tinder_token to make requests
		if self.last_auth_at:
			time_elapsed = (datetime.now() - self.last_auth_at) # time as datetime object
			time_elapsed = timeElapsed.total_seconds()
			time_boundary = 86400 # 24 hours -- time to auth again
			return (timeElapsed / time_boundary) > 1
		return True # First iteration

	def update_token(self,token):
		r = open('config.py','r')
		new_file = ['tinder_token = "{}"\n'.format(token)]
		for i,l in enumerate(r):
			if i != 0:
				new_file.append(l)
		r.close()
		r = open('config.py','w')
		for l in new_file:
			r.write(l)
		r.close()

	def handle_authentication(self):
		emailer = EmailSender()
		emailer.connect()
		emailer.make_alert_email()
		emailer.send_email()
		emailer.disconnect()
		while not self.isLucasOn():
			time.sleep(10)
		log_code = sendCode(config.lucas_phone_number)
		try:
			r = requests.get(config.aws_host + '/auth_code')
		except Exception as e:
			print(e)
			print("ERROR CONNECTING WITH LUCAS")
		else:
			response = r.json()
			new_token = getToken(config.lucas_phone_number, response['sms_code'], log_code)
			self.update_token(new_token)
			time.sleep(5)
			try:
				tr = tinder_api.get_self()
				while 'error' in tr:
					tell_lucas = requests.get(config.aws_host + '/failure')
					log_code = sendCode(config.lucas_phone_number)
					r = requests.get(config.aws_host + '/auth_code')
					response = r.json()
					new_token = getToken(config.lucas_phone_number, response['sms_code'], log_code)
					self.update_token(new_token)
					time.sleep(5)
					tr = tinder_api.get_self()
				tell_lucas = requests.get(config.aws_host + '/success')
				print("NEW TOKEN UPDATED SUCCESSFULLY")
			except:
				print('WIERD ERROR')	


			
		

			
	def run(self):
		while True:
			if self.isAuthTime():
				self.handle_authentication()
			if self.isSwipeTime():
				self.swipe_right()
			self.update()
			time.sleep(10)	


bot = TinderBot()
bot.run()		
					






