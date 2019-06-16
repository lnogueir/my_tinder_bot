from flask import Flask, jsonify, request
from helpers import create_message

server = Flask(__name__)

@server.route('/match', methods = ['POST'])
def match_response():
	match_info = request.get_json()
	print(match_info)
	print("Hello Lucas, I have recently emailed you about your new match with " + match_info[0]['name'] + ", " + match_info[0]['age'] + ".")
	print("Please answer the following questions:\n")
	will_unmatch = input("Would you like to unmatch her? ")
	while will_unmatch != 1 and will_unmatch != 0 and will_unmatch != '1' and will_unmatch != '0':
		will_unmatch = input("Invalid input, please enter 1 or 0:\n")
	answer = bool(int(will_unmatch))
	if answer:
		return jsonify({"will_unmatch" : 1, "girl_type" : None, "send_automatic" : None, "message" : None})
	girl_type = input("Is the girl slut or nerd? ")
	while girl_type.lower() != "slut" and girl_type.lower() != "nerd":
		girl_type = input("Enter a valid type: (slut or nerd)\n")
	isAutomatic = input("Should I sent her an automatic message? ")
	while isAutomatic != '1' and isAutomatic != '0' and isAutomatic != 0 and isAutomatic != 1:
		isAutomatic = input("Invalid input, please enter 1 or 0:\n")
	answer = int(isAutomatic)
	if answer:
		return jsonify({"will_unmatch" : 0, "girl_type" : girl_type, "send_automatic" : answer, "message" : create_message(match_info['name'], girl_type)})
	message = input("Enter manually the message you would want to send:\n")
	return 	jsonify({"will_unmatch" : 0, "girl_type" : girl_type, "send_automatic" : answer, "message" : message})	

@server.route('/auth_code')
def authentication_response():
	sms_code = input("Hey Lucas! It is time to update your tinder_token. Please enter the code we've sent you via SMS:\n")
	return jsonify({"sms_code" : sms_code})


@server.route('/failure')
def failure():
	input("OPERATION FAILED -- WE WILL REDO THE OPERATION.\nType something to agree.")
	return jsonify({"failure":"Got it"})	


@server.route('/success')
def success():
	print("SUCCESSFUL OPERATION")
	return jsonify({"success":"Got it"})

@server.route('/')
def is_active():
	return "<h1>TOMEM NO SEUS CU</h1>"


if __name__=='__main__':
        server.run(host='0.0.0.0',port=80,debug=True)



