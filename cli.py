import requests
import json
import sched, time
import dropbox
import os
import sys
import random
import shutil

def cls():
	os.system('cls' if os.name=='nt' else 'clear')
	print('(c) 2018 Snep Corporation. All rights reserved.\n')


# credentials = {
# 	'dropboxAccessToken' : 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
# 	'telegramAccessToken' : 'yyyyyyyyy:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
# 	'telegramChannel' : -yyyyyyyyyyyyy,
# 	'telegramBotID' : yyyyyyyyy,
# 	'twitter' : {
# 		'consumerKey' : 'xxxxxxxxxxxxxxxxxxxxxxxxx',
# 		'consumerSecret' : 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
# 		'accessTokenKey' : 'yyyyyyyyyyyyyyyyyyy-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
# 		'accessTokenSecret' : 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
# 	}
# }
# credentials are now saved in credentials.json in the format above

# initialize the dropbox folder
dbx = ''
# enter your dropbox access token in the ('') above

# telegram bot auth token (given by @BotFather upon your bot's creation)
token = ''
# enter your telegram bot's auth token in the '' above

# the chat_id of the channel where all the pictures will be posted
channel = 0
# enter your telegram channel's chat_id after the = above

# the id of the bot itself
botID = 0
# enter your telegram bot's id after the = above

# initialize twitter
api = ''

print('loading credentials.', end='', flush=True)
with open('credentials.json') as userinfo :
	credentials = json.load(userinfo)
	dbx = dropbox.Dropbox(credentials['dropboxAccessToken'])
	token = credentials['telegramAccessToken']
	channel = credentials['telegramChannel']
	botID = credentials['telegramBotID']
print('..success.')

# initialize all the lists and variables
files = []
usedIDs = []
forwardList = []
forwardInfoList = []
newForwardList = []
lastUpdateID = 000
rand = random.seed()

command = ''
commandList = ['>refresh CLI', 'getMe', 'getChat', 'getChatAdministrators', 'getUpdates', 'sendMessage', 'sendPhoto', 'messageAll', 'photoAll', 'forwardAll', 'getFile']
optionalCommandsList = {}
optionalCommandsList['getChat'] = ['>send request', 'chat_id']
optionalCommandsList['getChatAdministrators'] = ['>send request', 'chat_id']
optionalCommandsList['getUpdates']  = ['>send request', '>clear updates', 'offset', 'limit', 'timeout']
optionalCommandsList['sendMessage'] = ['>send request', 'chat_id', 'text', 'parse_mode', 'disable_web_page_preview', 'disable_notification', 'reply_to_message_id', 'reply_markup']
optionalCommandsList['sendPhoto']   = ['>send request', 'chat_id', 'photo', 'caption', 'disable_notification', 'reply_to_message_id']
optionalCommandsList['parse_mode'] = ['Markdown', 'HTML']
optionalCommandsList['disable_web_page_preview'] = ['true', 'false']
optionalCommandsList['disable_notification'] = ['true', 'false']
optionalCommandsList['messageAll'] = ['>send request', 'text', 'parse_mode', 'disable_web_page_preview', 'disable_notification']
optionalCommandsList['photoAll']   = ['>send request', 'photo', 'caption']
optionalCommandsList['forwardAll'] = ['>send request', 'message_id']
optionalCommandsList['getFile'] = ['>send request', 'file_id']

fileToDownload = {}




def startup() :
	cls()

	currenttime = (time.time())
	
	noowtime = ''
	if time.localtime(currenttime).tm_hour < 10 : noowtime = noowtime + '0'
	noowtime = noowtime + str(time.localtime(currenttime).tm_hour) + ':'
	if time.localtime(currenttime).tm_min  < 10 : noowtime = noowtime + '0'
	noowtime = noowtime + str(time.localtime(currenttime).tm_min)
	
	print('current time:', noowtime)
	
	#reinitialize all the lists and variables as global
	global token
	global botID
	global files
	global usedIDs
	global forwardList
	global newForwardList
	
	print('downloading files.json')
	dbxfiles = dbx.files_download('/files.json')
	files = dbxfiles[1].json()
	print(len(files), 'files')
	
	print('downloading usedIDs.json')
	dbxusedIDs = dbx.files_download('/usedIDs.json')
	usedIDs = dbxusedIDs[1].json()
	print(len(usedIDs), 'used ids')
	
	optionalCommandsList['photo'] = usedIDs
	optionalCommandsList['photo'].insert(0, 'random')
	optionalCommandsList['photo'].append('random')
	optionalCommandsList['file_id'] = []
	for i in range(len(files)) :
		optionalCommandsList['file_id'].append(files[i]['file_id'])
	report_forwards()
	print()
#





def report_forwards() :
	#print('report_forwards()')
	global token
	global forwardList
	global forwardInfoList
	
	forwardInfoList = []
	print('downloading forwardList.json')
	dbxforward = dbx.files_download('/forwardList.json')
	forwardList = dbxforward[1].json()
	print(len(forwardList), 'forwards')
	newForwardList = ['send request']
	for i in range(len(forwardList)):
		newForwardList.append(str(forwardList[i]))
	optionalCommandsList['chat_id']  = newForwardList

	request = 'https://api.telegram.org/bot' + token + '/getChat'
	
	print()
	for i in range(len(forwardList)):
		response = requests.get(request, {'chat_id': forwardList[i]})
		response = response.json()
		if response['ok'] :
			print('forward[', str(i+1),']: (', str(response['result']['id']), ') ', response['result']['title'], sep='')
			forwardInfoList.append('(' + str(response['result']['id']) + ') ' + response['result']['title'])
		else :
			print('forward[', str(i+1),']: (', str(forwardList[i]), ') ', response['description'], sep='')
			forwardInfoList.append('(' + str(forwardList[i]) + ') ' + response['description'])
	print('done.')
#





def parse_request() :
	#print('parse_request()')
	global command
	global lastUpdateID
	global forwardList
	global fileToDownload

	print()
	areyousure = request = ''
	areyousure = input('Are you sure? Y/n>')
	if areyousure == 'y' or areyousure == '' :
		if '/messageAll' in command :
			for i in range(len(forwardList)):
				print('sending to forward[' + str(i) + '](' + str(forwardList[i]) + ')...', end='')
				response = requests.get(command.replace('/messageAll?', '/sendMessage?chat_id=' + str(forwardList[i]) + '&'))
				#response = response.json()
				#response = {}
				#response['ok'] = True
				if response.json()['ok'] :
					print('success.\n', end='')
				else :
					print('failed (' + response.json()['description'] + ')(' + response.url + '), retrying...', end='')
					response = requests.get(command.replace('/messageAll?', '/sendMessage?chat_id=' + str(forwardList[i]) + '&'))
					response = response.json()
					if response['ok'] :
						print('success.\n', end='')
					else :
						print('failed.\n', end='')
		elif '/photoAll' in command :
			for i in range(len(forwardList)):
				print('sending to forward[' + str(i) + '](' + str(forwardList[i]) + ')...', end='')
				response = requests.get(command.replace('/photoAll?', '/sendPhoto?chat_id=' + str(forwardList[i]) + '&'))
				#response = response.json()
				#response = {}
				#response['ok'] = True
				if response.json()['ok'] :
					print('success.\n', end='')
				else :
					print('failed (' + response.json()['description'] + ')(' + response.url + '), retrying...', end='')
					response = requests.get(command.replace('/photoAll?', '/sendPhoto?chat_id=' + str(forwardList[i]) + '&'))
					response = response.json()
					if response['ok'] :
						print('success.\n', end='')
					else :
						print('failed.\n', end='')
		elif '/forwardAll' in command :
			command = command.replace('/forwardAll?', '/forwardMessage?from_chat_id=' + str(channel) + '&')
			for i in range(len(forwardList)):
				print('sending to forward[' + str(i) + '](' + str(forwardList[i]) + ')...', end='')
				response = requests.get(command + '&chat_id=' + str(forwardList[i]))
				if response.json()['ok'] :
					print('success.\n', end='')
				else :
					print('failed (' + response.json()['description'] + ')(' + response.url + '), retrying...', end='')
					response = requests.get(command + '&chat_id=' + str(forwardList[i]))
					response = response.json()
					if response['ok'] :
						print('success.\n', end='')
					else :
						print('failed.\n', end='')
		elif '/getFile' in command :
			response = requests.get(command)
			response = response.json()
			if response['ok'] :
				print('response: ok')
				print('downloading...')
				request = 'https://api.telegram.org/file/bot' + token + '/' + response['result']['file_path']
				response = requests.get(request, stream=True) # stream=True IS REQUIRED
				filename = fileToDownload['file_name']
				if response.status_code == 200:
					with open(filename, 'wb') as image:
						shutil.copyfileobj(response.raw, image)
				print(' saved as ' + filename)
		else :
			response = requests.get(command)
			response = response.json()
			if '/getUpdates' in command and response['ok'] and len(response['result']) > 0:
				lastUpdateID = response['result'][len(response['result']) - 1]['update_id']
			print('\nresponse:')
			print_json_formatted(response)
			print('(' + str(len(response['result'])) + ')')
	print('done.')
#





def take_input() :
	global command
	command = ''
	
	print('\n')
	for i in range(len(commandList)) :
		print('[' + str(i) + ']' + commandList[i])
	print('\nenter your command below or enter a number from the list.\nall requests will be formatted like so:\n    https://api.telegram.org/bot <token> /COMMAND')
	command = input('>')
	if IsInt(command) and int(command) < 0 :
		sys.exit()
	if parse_command() :
		command = 'https://api.telegram.org/bot' + token + '/' + command
		print()
		print(command)
		parse_request()





# https://stackoverflow.com/a/1267145/8197207
def IsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False





def parse_command() :
	#print('parse_command()')
	global command
	global commandList
	global lastUpdateID
	global fileToDownload
	
	tempCommand = command
	
	if tempCommand.isdigit() and int(command) < len(commandList) :
		if int(command) == 0 : 
			startup()
			return False
		command = tempCommand = commandList[int(command)]
	continueLooping = True
	while continueLooping :
		print('\n')
		if command in optionalCommandsList :
			for i in range(len(optionalCommandsList[command])) :
				print('[' + str(i) + ']' + optionalCommandsList[command][i])
		else :
			print('[0]>send request')
		print('\nenter your command below or enter a number from the list.\nall requests will be formatted like so:\n    https://api.telegram.org/bot <token> /COMMAND?OPTIONAL=VALUE&OPTIONAL=VALUE')
		print('\ncurrent command: ' + tempCommand)
		optionalCommand = input(tempCommand + '>')
		
		if optionalCommand.isdigit() and int(optionalCommand) == 0 :
			continueLooping = False
			command = tempCommand
		elif optionalCommand == '':
			continueLooping = False
			command = tempCommand
		else :
			if optionalCommand.isdigit() and int(optionalCommand) < len(optionalCommandsList[command]) :
				optionalCommand = optionalCommandsList[command][int(optionalCommand)]
				
			#PUT NONSTANDARD COMMAND LISTS HERE!		##########
			if optionalCommand == 'chat_id' :
				print()
				for i in range(len(forwardList)):
					print('forward[', str(i+1),']: ', forwardInfoList[i], sep='')
			elif optionalCommand == 'file_id' :
				print()
				for i in range(len(files)) :
					print('files[', str(i),']: ', files[i]['file_name'], sep='')
			elif optionalCommand == '>clear updates' :
				command = tempCommand = tempCommand + '?offset=' + str(lastUpdateID + 1)
				return True
			#end nonstandard commands					##########
			if optionalCommand in optionalCommandsList :
				print()
				for i in range(len(optionalCommandsList[optionalCommand])) :
					print('[' + str(i) + ']' + optionalCommandsList[optionalCommand][i])
				print('\nenter your command below or enter a number from the list.')
				if '?' in tempCommand :
					optionalCommandValue = input(tempCommand + '&' + optionalCommand + '>')
				else :
					optionalCommandValue = input(tempCommand + '?' + optionalCommand + '>')
				
				if optionalCommandValue == '' and len(optionalCommandsList[optionalCommand]) > 0 :
					optionalCommandValue = optionalCommandsList[optionalCommand][0]
				elif optionalCommand == 'file_id' and optionalCommandValue.isdigit() and int(optionalCommandValue) < len(files) :
					fileToDownload = files[int(optionalCommandValue)]
					optionalCommandValue = optionalCommandsList[optionalCommand][int(optionalCommandValue)]
				elif optionalCommandValue.isdigit() and int(optionalCommandValue) < len(optionalCommandsList[optionalCommand]) :
					optionalCommandValue = optionalCommandsList[optionalCommand][int(optionalCommandValue)]
			else :
				if '?' in tempCommand :
					optionalCommandValue = input(tempCommand + '&' + optionalCommand + '>')
				else :
					optionalCommandValue = input(tempCommand + '?' + optionalCommand + '>')
			
			#PUT NONSTANDARD COMMAND LISTS HERE!		##########
			if optionalCommandValue == 'random' :
				randomint = random.randint(0, len(optionalCommandsList[optionalCommand]) - 2)
				print(randomint)
				optionalCommandValue = optionalCommandsList[optionalCommand][randomint]
			#end nonstandard commands					##########
			
			if '?' in tempCommand :
				tempCommand = tempCommand + '&' + optionalCommand + '=' + optionalCommandValue
			else :
				tempCommand = tempCommand + '?' + optionalCommand + '=' + optionalCommandValue

			optionalCommand = ''
			optionalCommandValue = ''
	#if optionalCommand.isdigit() and int(optionalCommandValue) < len(optionalCommandsList[command]) :
	#	optionalCommand = '&' + optionalCommand + '=' + optionalCommandsList[command][optionalCommandValue]
	#print(command)
	return True
#





def print_json_formatted(jsonToPrint) :
	#print('print_json_formatted(jsonToPrint)')
	#indent = ''
	#indentIncrement = '    '
	
	#stringVar = json.dumps(jsonToPrint)
	#for c in stringVar :
	#	if c == '{' :
	#		print('\n' + indent + '{\n' + indent + indentIncrement, end='')
	#		indent = indent + indentIncrement
	#	elif c == '}' :
	#		indent = indent[:-len(indentIncrement)]
	#		print('\n' + indent + '}', end='')
	#	elif c == '[' :
	#		print('\n' + indent + '[', end='')
	#		indent = indent + indentIncrement
	#	elif c == ']' :
	#		indent = indent[:-len(indentIncrement)]
	#		print('\n' + indent + ']', end='')
	#	elif c == ',' :
	#		print(',\n' + indent[:-1], end='')
	#	#elif c == '\n' :
	#	#	print(indent)
	#	else :
	#		print(c, end='')
	print(json.dumps(jsonToPrint, indent=2, sort_keys=True))
	print()
#





startup()
while True:
	take_input()
