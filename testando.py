import tinder_api
import requests
import os

# r = open('config.py','r')
# new_file = ['tinder_token = "{}"\n'.format(123456)]
# for i,l in enumerate(r):
# 	if i != 0:
# 		new_file.append(l)
# r.close()
# r = open('config.py','w')
# for l in new_file:
# 	r.write(l)
# r.close()		

# url = "http://3.92.239.193:80/match"
# r = requests.get(url)
# response = r.json()
# print(type(response['will_unmatch']))

##Opens all my recommendeds photos on browse 
# import webbrowser
# try:
# 	recommendations = tinder_api.get_recs_v2()['data']['results']
# 	for i,rec in enumerate(recommendations):
# 		photos = rec['user']['photos']
# 		girl_id = rec['user']['_id']
# 		print(tinder_api.like(girl_id))
# 		for photo in photos:
# 			url = photo['processedFiles'][0]['url']
# 			webbrowser.open_new_tab(url)
# 		break	
# except:
# 	print('ERROR')	
##

## Getting messages from match
# matches = tinder_api.get_updates()['matches']
# for match in matches:
# 	print([message['message'] for message in match['messages']])
	# for message in match['messages']:
	# 	print(message['message'])
##

## Sending message to match
# match_id = tinder_api.get_updates()['matches'][0]['_id']
# msg = tinder_api.send_msg(match_id,'Oi tetinha, estou mandando essa mensagem pelo python, creu.')
# print(msg)
##

## Lucas liking Matheus
# print(tinder_api.like('531f5b525322c5b615001bc1'))
##

## Matheus liking Lucas
# print(tinder_api.like('5d0081523f4ac515009490af'))
##

## Get user info
try:
	print(tinder_api.get_self())
except:
	print("cu")
## Get updates
# print(tinder_api.get_updates())


