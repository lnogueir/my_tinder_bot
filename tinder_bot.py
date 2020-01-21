
import config, tinder_api 
from emailer import Emailer
from helpers import get_girls_age, create_message, get_her_messages, get_my_messages
from phone_auth_token import sendCode, getToken
from automatic_messages import AUTOMATIC_MESSAGES
from datetime import datetime
import os, csv, time
import json, requests


## AFTER I NEED TO MAKE CLASSES FOR THESE BIG MEMBER VARIABLES

class TinderBot:
	def __init__(self):
		self.statistics	= {'total_matches' : 0, 'swipes': 0, 'cur_matches': 0, 'match_rate' : 0}
		statistics_path = 'tinder_statistics.csv'
		if os.path.exists(statistics_path): # Get current statistics
			with open(statistics_path, newline='') as csvfile:
				csv_data = csv.reader(csvfile, delimiter=' ', quotechar='|')
				for row in csv_data:
			 		self.statistics[row[0]] = float(row[1])
		else:
			open(statistics_path,'w').close()	 					 			 		
		self.current_matches = [] 
		match_ids_path = "match_ids.txt" # Get already existing matches
		if os.path.exists(match_ids_path):
			with open(match_ids_path, 'r') as ids_file:
				for _id in ids_file:
			 		self.current_matches.append(_id.rstrip("\n\r")) 
		else:
			open(match_ids_path,'w').close()	 					 		
		self.account_token = config.tinder_token
		self.matches = {}
		self.last_like_at = None
		self.last_auth_at = None
		track_time = "track_time.txt"
		if os.path.exists(track_time) and os.stat(track_time).st_size != 0:
			with open(track_time, 'r') as track_f:
				for i,time in enumerate(track_f): # this iterate only twice
					if i == 0:
						self.last_like_at = datetime.strptime(time.split('@')[1].rstrip('\n\r'), '%m/%d/%y %H:%M:%S')
					if i == 1:
						self.last_auth_at = datetime.strptime(time.split('@')[1].rstrip('\n\r'), '%m/%d/%y %H:%M:%S')		
		else:
			f = open(track_time,'w')
			f.write('last_liked@none\n')
			f.write('last_auth@none\n')
			f.close()				
		self.emailer = Emailer()


	def fix_time_file(self): # True if fixing liking time, false if auth time
		date_time = datetime.now().strftime('%m/%d/%y %H:%M:%S')
		f = open('track_time.txt','r')
		l=[]
		for line in f:
			l.append(line.split('@'))
		f.close()
		f = open('track_time.txt','w')
		l[0][1] = self.last_like_at.strftime('%m/%d/%y %H:%M:%S') if self.last_like_at else None
		l[1][1] = self.last_auth_at.strftime('%m/%d/%y %H:%M:%S') if self.last_auth_at else None
		for line in l:
			append_to_file = line[1] if line[1] else 'none'
			f.write(line[0]+'@'+append_to_file+'\n')
		f.close()	



	def isSwipeTime(self):
		if self.last_like_at:
			time_elapsed = (datetime.now() - self.last_like_at) # time as datetime object
			time_elapsed = time_elapsed.total_seconds()
			time_boundary = 21600 # 12 hours -- time to swipe again
			return (time_elapsed / time_boundary) > 1
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
			print('LUCAS IS NOT CONNECTED')
			return False
		else:
			print('LUCAS IS CONNECTED')
			return True	    


	def swipe_right(self):
		LIKES_LIMIT = 45 #Tinder has a limit of 100 like per 12 hours, like 45/6 hours so we are safe.
		try:
			track_iterator = 0
			while track_iterator <= LIKES_LIMIT:
				recommendations = tinder_api.get_recs_v2()['data']['results']
				for rec in recommendations:
					girl_id = rec['user']['_id']
					try:
						like_response = tinder_api.like(girl_id)
					except:
						print('WHATS HAPPENING')
						return	
					print('LIKED')
					self.statistics['swipes']+=1
					track_iterator+=1 
					if track_iterator == LIKES_LIMIT: # Check if its time to stop liking
						self.last_like_at = datetime.now()
						self.fix_time_file()
						self.update_statistics_file()
						break
										
					time.sleep(10)	
			print('DONE LIKING')		
		except:
			print('COULD NOT FINISH LIKING')


	def isNewMatch(self,match_id):
		return match_id not in self.current_matches


	def fix_id_file(self):
		open('match_ids.txt','w').close()
		f = open('match_ids.txt','a')
		for _id in self.current_matches:
			f.write(str(_id)+'\n')
		f.close()


	def onMatch(self,match):  
## onMatch will be called always if its the first iteration, so we update self.match before check if is new match
		girl = match['person']
		bio = girl['bio'] if 'bio' in girl else ''
		self.matches[match['_id']] = {
			'name': girl['name'],
			'age': get_girls_age(datetime.now(), girl['birth_date']),
			'messages': {message_obj['message']:i for i, message_obj in enumerate(match['messages'])},
			'photos': [photo_obj['processedFiles'][0]['url'] for photo_obj in girl['photos']], # get url for each photo of the girl
			'bio': bio
		}
		if self.isNewMatch(match['_id']): ## New match!!
			self.statistics['total_matches']+=1
			self.statistics['match_rate'] = self.statistics['total_matches'] / self.statistics['swipes'] if self.statistics['swipes'] != 0 else 0
			self.update_statistics_file()
			f = open('match_ids.txt','a')
			f.write(str(match['_id'])+'\n')
			f.close() # updates ids file
			self.current_matches.append(str(match['_id']))
			girl = self.matches[match['_id']]
			self.emailer.connect() # Email Lucas about new match
			self.emailer.make_email(girl,'match')
			self.emailer.send_email()
			self.emailer.disconnect()
			print('NEW MATCH')
			while not self.isLucasOn():
				time.sleep(10)
			try:
				url = config.aws_host + "/match"
				json_data = {"name": girl['name'], "age":str(girl['age'])}
				r = requests.post(url, json = json_data)
				response = r.json()
			except Exception as e:
				print(e)	
				return {"error": "Something went wrong when trying to communicate with Lucas."}
			if bool(int(response["will_unmatch"])): # unmatch person 
				match_id = match['_id']
				self.current_matches.remove(match_id)
				self.fix_id_file()
				del self.matches[match_id]
				return tinder_api.unmatch(match_id)
			else:					
				return tinder_api.send_msg(match['_id'], response['message'])
			
					

	def onNewMessage(self, new_messages, match_id):
		her_messages = get_her_messages(self.matches[match_id]['name'], new_messages)
		my_messages = get_my_messages(self.matches[match_id]['name'], new_messages)
		did_she_text_last = (her_messages[-1] == new_messages[-1]) if (len(her_messages) != 0) else False
		if 'WRONG HOLE' in her_messages or 'WIERD' in her_messages: # unmatch person
			print('ARE YOU HERE FOR REAL?')
			self.current_matches.remove(match_id)
			self.fix_id_file()
			del self.matches[match_id]
			return tinder_api.unmatch(match_id)
		if 'MORE' == her_messages[-1]:
				tinder_api.send_msg(match_id,create_message(self.matches[match_id]['name'], "more"))
				print("MORE MESSAGE SENT")	
		if did_she_text_last and AUTOMATIC_MESSAGES['YES DADDY'].rstrip('\n\r') not in my_messages:	# This means that I am talking to her now
			if 'YES DADDY' in her_messages or 'LETS GO' in her_messages:
				tinder_api.send_msg(match_id,create_message(self.matches[match_id]['name'],"YES DADDY"))
				print("NEW DATE FOUND -- YES DADDY MESSAGE SENT")
				self.emailer.connect() # Tell Lucas about new date
				girl = self.matches[match_id]
				self.emailer.make_email(girl,'date')
				self.emailer.send_email()
				self.emailer.disconnect()
			else: 
				tinder_api.send_msg(match_id,create_message(self.matches[match_id]['name'],"invalid_reply"))			
				print("INVALID REPLY MESSAGE SENT")

	def update(self):
		try:
			matches = tinder_api.get_updates()['matches']		
		except:
			print('COULD NOT UPDATE')
		time.sleep(1)	
		self.statistics['cur_matches'] = len(matches)
		for match in matches:
			match_id = match['_id']
			if match_id not in self.matches: # new match!				
				self.onMatch(match)
			else:
				new_messages = [message_obj['message'] for message_obj in match['messages']]
				old_messages = self.matches[match_id]['messages']
				if self.matches[match_id] and old_messages != new_messages: # new message!
					self.onNewMessage(new_messages,match_id)

	def isAuthTime(self): # Every 24 hours we need a new tinder_token to make requests
		if self.last_auth_at:
			time_elapsed = (datetime.now() - self.last_auth_at) # time as datetime object
			time_elapsed = time_elapsed.total_seconds()
			time_boundary = 86400 # 24 hours -- time to auth again
			return (time_elapsed / time_boundary) > 1
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
		self.emailer.connect() # Tell Luca to get SMS code
		self.emailer.make_alert_email()
		self.emailer.send_email()
		self.emailer.disconnect()
		while not self.isLucasOn():
			time.sleep(10)
		print("SENDING SMS...")	
		log_code = sendCode(config.lucas_phone_number)
		try:
			r = requests.get(config.aws_host + '/auth_code')
		except Exception as e:
			print(e)
			print("ERROR CONNECTING WITH LUCAS")
		else:
			response = r.json()
			new_token = getToken(str(config.lucas_phone_number), str(response['sms_code']), log_code)	
			self.update_token(new_token)
			time.sleep(5)
			try:
				tr = tinder_api.get_self()
				while 'error' in tr:
					print('ERROR WITH TOKEN')
					tell_lucas = requests.get(config.aws_host + '/failure')
					log_code = sendCode(config.lucas_phone_number)
					r = requests.get(config.aws_host + '/auth_code')
					response = r.json()
					new_token = getToken(str(config.lucas_phone_number), str(response['sms_code']), log_code)
					self.update_token(new_token)
					time.sleep(5)
					tr = tinder_api.get_self()
				tell_lucas = requests.get(config.aws_host + '/success')
				print("NEW TOKEN UPDATED SUCCESSFULLY")
				self.last_auth_at = datetime.now()
				self.fix_time_file()
			except:
				print('ERROR AUTHENTICATING')
				exit()	

			
	def run(self):
		while True:
			if self.isAuthTime():
				self.handle_authentication()
			if self.isSwipeTime():
				self.swipe_right()
			print('UPDATING')	
			self.update()
			time.sleep(10)	


bot = TinderBot()
bot.run()		
					






