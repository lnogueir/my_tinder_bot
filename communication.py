from flask import Flask, jsonify, request
from helpers import create_message

server = Flask(__name__)

@server.route('/match', methods = ['POST'])
def match_response():
	match_info = request.get_json()
	print("Hello Lucas, I have recently emailed you about your new match with " + match_info['name'] + ", " + match_info['age'] + ".")
	print("Please answer the following questions:\n")
	will_unmatch = raw_input("Would you like to unmatch her? ")
	while will_unmatch != 1 and will_unmatch != 0 and will_unmatch != '1' and will_unmatch != '0':
		will_unmatch = raw_input("Invalid input, please enter 1 or 0:\n")
	answer = bool(int(will_unmatch))
	if answer:
		return jsonify({"will_unmatch" : 1, "message" : None})
	girl_type = raw_input("Is the girl slut or nerd? ")
	while girl_type.lower() != "slut" and girl_type.lower() != "nerd":
		girl_type = raw_input("Enter a valid type: (slut or nerd)\n")
	isAutomatic = raw_input("Should I sent her an automatic message? ")
	while isAutomatic != '1' and isAutomatic != '0' and isAutomatic != 0 and isAutomatic != 1:
		isAutomatic = raw_input("Invalid input, please enter 1 or 0:\n")
	answer = int(isAutomatic)
	if answer:
		return jsonify({"will_unmatch" : 0, "message" : create_message(match_info['name'], girl_type)})
	message = raw_input("Enter manually the message you would want to send:\n")
	return 	jsonify({"will_unmatch" : 0, "message" : message})	

@server.route('/auth_code')
def authentication_response():
	sms_code = raw_input("Hey Lucas! It is time to update your tinder_token. Please enter the code we've sent you via SMS:\n")
	return jsonify({"sms_code" : sms_code})


@server.route('/failure')
def failure():
	raw_input("OPERATION FAILED -- WE WILL REDO THE OPERATION.\nType something to agree.")
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



