from flask import Flask, jsonify, request
from helpers import create_message

server = Flask(__name__)

@server.route('/match',methods=['GET', 'POST'])
def match_response():
	# match_info = request.get_json()
	# print("Hello Lucas, I have recently emailed you about your new match with " + match_info['name'] + ", " + match_info['age'] + ".")
	print("Please answer the following questions:\n")
	will_unmatch = input("Would you like to unmatch her? ")
	while will_unmatch != '1' and will_unmatch != '0':
		print(will_unmatch,type(will_unmatch))
		will_unmatch = input("Invalid input, please enter 1 or 0:\n")
	answer = bool(int(will_unmatch))
	if answer:
		return jsonify({"will_unmatch" : 1, "girl_type" : None, "send_automatic" : None, "message" : None})
	girl_type = input("Is the girl slut or nerd? ")
	while girl_type.lower() != "slut" and girl_type.lower() != "nerd":
		girl_type = input("Enter a valid type: (slut or nerd)\n")
	isAutomatic = input("Should I sent her an automatic message? ")
	while isAutomatic != '1' and isAutomatic != '0':
		isAutomatic = input("Invalid input, please enter 1 or 0:\n")
	answer = int(isAutomatic)
	if answer:
		return jsonify({"will_unmatch" : 0, "girl_type" : girl_type, "send_automatic" : answer, "message" : create_message(match_info['name'], girl_type)})
	message = input("Enter manually the message you would want to send:\n")
	return 	jsonify({"will_unmatch" : 0, "girl_type" : girl_type, "send_automatic" : answer, "message" : message})	


if __name__=='__main__':
        server.run(port=5000,debug=True)
