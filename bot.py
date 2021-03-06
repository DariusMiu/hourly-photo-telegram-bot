try : import ujson as json
except : import json
import requests
import sched, time
import dropbox
import twitter
import shutil

# initialize the dropbox folder
dbx = ''

# telegram bot auth token (given by @BotFather upon your bot's creation)
token = ''

# the chat_id of the channel where all the pictures will be posted
channel = 0

# the id of the bot itself
botID = 0

# initialize twitter
api = ''

# credentials = {
# 	"dropboxAccessToken" : "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
# 	"telegramAccessToken" : "yyyyyyyyy:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
# 	"telegramChannel" : -yyyyyyyyyyyyy,
# 	"telegramBotID" : yyyyyyyyy,
# 	"twitter" : {
# 		"consumerKey" : "xxxxxxxxxxxxxxxxxxxxxxxxx",
# 		"consumerSecret" : "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
# 		"accessTokenKey" : "yyyyyyyyyyyyyyyyyyy-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
# 		"accessTokenSecret" : "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
# 	}
# }
# credentials are saved in credentials.json in the format above

# what to send to twitter in addition to the link (make sure encoding is utf-8)
load = '' # remember to include whitespace at the end (newline or space)

print('loading credentials...', end='')
with open('credentials.json') as userinfo :
	credentials = json.load(userinfo)
	dbx = dropbox.Dropbox(credentials['dropboxAccessToken'])
	token = credentials['telegramAccessToken']
	channel = credentials['telegramChannel']
	botID = credentials['telegramBotID']
	api = twitter.Api(consumer_key = credentials['twitter']['consumerKey'], consumer_secret = credentials['twitter']['consumerSecret'], access_token_key = credentials['twitter']['accessTokenKey'], access_token_secret = credentials['twitter']['accessTokenSecret'])
	#print(json.dumps(credentials, indent=2))
print('success.')

print('loading load.txt...', end='')
try :
	with open('load.txt', 'r', encoding='utf-8') as twitterload :
		load = twitterload.read()
	print('success.')
except : print('failed. (no load available)')

#initialize the scheduler
scheduler = sched.scheduler(time.time, time.sleep)

#initialize all the lists and variables
admins = []
files = []
usedIDs = []
forwardList = []
delay = 180
timezone = -5
report = ''
sendReport = False



def update():
	print()
	#reinitialize all the lists and variables as global
	global token
	global botID
	global admins
	global files
	global usedIDs
	global forwardList
	global delay
	global timezone
	global report
	global sendReport	
	report = ''
	
	print('reading admins.json... ', end='')
	dbxadmins = dbx.files_download('/admins.json')
	admins = dbxadmins[1].json()
	print(len(admins), 'admins')
	
	print('reading files.json... ', end='')
	dbxfiles = dbx.files_download('/files.json')
	files = dbxfiles[1].json()
	print(len(files), 'files')
	
	print('reading usedIDs.json... ', end='')
	dbxusedIDs = dbx.files_download('/usedIDs.json')
	usedIDs = dbxusedIDs[1].json()
	print(len(usedIDs), 'used ids')
	
	print('reading forwardList.json... ', end='')
	dbxforward = dbx.files_download('/forwardList.json')
	forwardList = dbxforward[1].json()
	print(len(forwardList), 'forwards')
	
	print('reading delay.json... ', end='')
	dbxdelay = dbx.files_download('/delay.json')
	delay = dbxdelay[1].json()
	print(delay, 'minute delay')

	print('reading timezone.json... ', end='')
	dbxtime = dbx.files_download('/timezone.json')
	timezone = dbxtime[1].json()
	print('UTC', timezone)

	print()
	
	print('getUpdates')
	request = 'https://api.telegram.org/bot' + token + '/getUpdates'
	response = requests.get(request)
	#print(response.url)
	response = response.json()
	if response['ok'] :
		print('response:', 'ok')
		updateList = response['result']
	else :
		print('response not ok')
		#BREAK

	print(' updates:', len(updateList))


	while len(updateList) > 0 :
		for i in range(len(updateList)):
			#print()
			print('update_id:', updateList[i]['update_id'], '|', end=' ')
			if 'message' in updateList[i] :
				#print('  chat id:', updateList[i]['message']['chat']['id'])
				if updateList[i]['message']['chat']['id'] in admins :
					if 'document' in updateList[i]['message']:
						print(json.dumps(updateList[i]['message']['document'], indent=2, sort_keys=True))
						if updateList[i]['message']['document'] in files :
							print('files already contains this photo')
						else:
							files.append(updateList[i]['message']['document'])
							print('file added', end=' ') 
							if 'from' in updateList[i]['message'] :
								if 'username' in updateList[i]['message']['from'] :
									print('(from ', updateList[i]['message']['from']['username'], ')', sep='')
								else :
									print('(from ', updateList[i]['message']['from']['first_name'], ' (', updateList[i]['message']['from']['id'], '))', sep='')
							else :
								print()
					else :
						#MESSAGE DOESN'T CONTAIN A FILE, PUT PARSE CODE HERE
						print('message does not contain a file', end=' ')
						#print(json.dumps(updateList[i], indent=2, sort_keys=True))
						if 'from' in updateList[i]['message'] :
							if 'username' in updateList[i]['message']['from'] :
								print('(from ', updateList[i]['message']['from']['username'], ')', sep='')
							else :
								print('(from ', updateList[i]['message']['from']['first_name'], ' (', updateList[i]['message']['from']['id'], '))', sep='')
						else :
							print()
				else :
					print('update not from admin', end=' ')
					if 'new_chat_member' in updateList[i]['message'] :
						if updateList[i]['message']['new_chat_member']['id'] == botID :
							forwardList.append(updateList[i]['message']['chat']['id'])
							if 'username' in updateList[i]['message']['from'] :
								print('\nadded ', updateList[i]['message']['chat']['title'], ' (', updateList[i]['message']['chat']['id'], ') to forwardList by ', str(updateList[i]['message']['from']['username']), ' (', updateList[i]['message']['from']['id'], ')', sep='')
								report = report + '`added `' + str(updateList[i]['message']['chat']['title']) + '` to forwardList by `%40' + str(updateList[i]['message']['from']['username']) + '\n'	# %40 = @
							else :
								print('\nadded ', updateList[i]['message']['chat']['title'], ' (', updateList[i]['message']['chat']['id'], ') to forwardList by ', str(updateList[i]['message']['from']), sep='')
								report = report + '`added `' + str(updateList[i]['message']['chat']['title']) + '` to forwardList by `' + str(updateList[i]['message']['from']['first_name']) + ' (' + str(updateList[i]['message']['from']['id']) + ')\n'
							sendReport = True
					elif 'left_chat_member' in updateList[i]['message'] :
						if updateList[i]['message']['left_chat_member']['id'] == botID :
							if updateList[i]['message']['chat']['id'] in forwardList :
								forwardList.remove(updateList[i]['message']['chat']['id'])
								print('\nremoved', updateList[i]['message']['chat']['title'], 'from forwardList')
								report = report + '`removed `' + str(updateList[i]['message']['chat']['title']) + ' `from forwardList`\n'
								sendReport = True
					else :			
						if 'from' in updateList[i]['message'] :
							if 'username' in updateList[i]['message']['from'] :
								print('(from ', updateList[i]['message']['from']['username'], ')', sep='')
							else :
								print('(from ', updateList[i]['message']['from']['first_name'], ' (', updateList[i]['message']['from']['id'], '))', sep='')
						else :
							print()
						print('   ', updateList[i]['message'])
			else :
				print('update not does not contain message')
				print(updateList[i])
		if len(updateList) > 0 :
			mostrecentupdate = updateList[len(updateList) - 1]['update_id']
			print('clearing updateList through to update_id', mostrecentupdate + 1)
			request = 'https://api.telegram.org/bot' + token + '/getUpdates'
			response = requests.get(request + '?offset=' + str(mostrecentupdate + 1))
			response = response.json()
			if response['ok'] :
				updateList = response['result']
				print(' updates:', len(updateList))
				if len(updateList) <= 0 :
					print('...success')
				else :
					print('updateList not empty, repeating...')
			else :
				print('failed')
				sendReport = True
	else :
		print('updateList empty')

	print()



def report_forwards() :
	print()
	global token
	global forwardList
	global report
	global admins
	report = ''
	
	print('reading forwardList.json')
	dbxforward = dbx.files_download('/forwardList.json')
	forwardList = dbxforward[1].json()
	print(len(forwardList), 'forwards')
	print()
	
	request = 'https://api.telegram.org/bot' + token + '/getChat'
	
	for i in range(len(forwardList)):
		response = requests.get(request + '?chat_id=' + str(forwardList[i]))
		response = response.json()
		if response['ok'] :
			print('forward[', str(i),']: (', str(response['result']['id']), ') ', response['result']['title'], sep='')
			report = report + '`forward[' + str(i) + ']: `' + response['result']['title'] + '\n'
		else :
			print('forward[', str(i),']: (', str(forwardList[i]), ') ', response['description'], sep='')
	
	#print('uploading forwardList.json to Dropbox')
	#dbx.files_upload(json.dumps(forwardList).encode('utf-8'), '/forwardList.json', dropbox.files.WriteMode('overwrite', None))
	
	#request = 'https://api.telegram.org/bot' + token + '/sendMessage'
	#for i in range(len(admins)):
	#	requests.get(request, {'chat_id': admins[i], 'text': report, 'parse_mode': 'Markdown'})
	
	#print(report)
	print()



def update_dropbox() :
	print()
	#reinitialize all the lists and variables as global
	global files
	global usedIDs
	global forwardList
	global delay

	print('uploading files.json to Dropbox')
	dbx.files_upload(json.dumps(files      ).encode('utf-8'), '/files.json',         dropbox.files.WriteMode('overwrite', None))
	print('uploading usedIDs.json to Dropbox')
	dbx.files_upload(json.dumps(usedIDs    ).encode('utf-8'), '/usedIDs.json',       dropbox.files.WriteMode('overwrite', None))
	print('uploading delay.json to Dropbox')
	dbx.files_upload(json.dumps(delay      ).encode('utf-8'), '/delay.json',         dropbox.files.WriteMode('overwrite', None))
	print('uploading forwardList.json to Dropbox')
	dbx.files_upload(json.dumps(forwardList).encode('utf-8'), '/forwardList.json',   dropbox.files.WriteMode('overwrite', None))
	print()



def post_photo():
	print()
	global token
	global channel
	global files
	global usedIDs
	global forwardList
	global report
	global sendReport
	global api
	global load
	removeList = []
	isImage = True
	forwardMessage = True
	postToTwitter = True
	
	if len(files) > 0 :
		fileToSend = files[0]
		filename = 'image'
		link = None
		request = 'https://api.telegram.org/bot' + token + '/getFile?file_id=' + fileToSend['file_id']
		#print(request)
		response = requests.get(request)
		response = response.json()
		if response['ok'] :
			if 'image' in fileToSend['mime_type'] :
				filename = filename + '.' + fileToSend['mime_type'][6:] # cuts off the first 6 characters ('image/')
			else :
				isImage = False
				mime_type = fileToSend['mime_type'].split('/')
				filename = filename + '.' + mime_type[1] # uses anything found after the slash
				if 'video' not in fileToSend['mime_type'] :
					postToTwitter = False
				elif fileToSend['file_size'] >= 5242880 : # 5MB in bytes
					postToTwitter = False
			#print("fileToSend['mime_type']:" + fileToSend['mime_type'])
			print('downloading...', end='')
			request = 'https://api.telegram.org/file/bot' + token + '/' + response['result']['file_path']
			response = requests.get(request, stream=True) # stream=True IS REQUIRED
			print('done.', end='')
			if response.status_code == 200:
				with open(filename, 'wb') as image:
					shutil.copyfileobj(response.raw, image)
			print(' saved as ' + filename)
			link = get_flickr_link(fileToSend['file_name'])
		else :
			print('response not ok')
			report = report + '`post failed.`\n`photo re-added to queue.`'
			return # we don't have a sendable file, so just return


		snep = open(filename, 'rb')

		# send to telegram
		if isImage :
			print('sending photo to telegram, chat_id:' + str(channel) + '...', end='')
			request = 'https://api.telegram.org/bot' + token + '/sendPhoto'
			telegramfile = {'photo': snep}
			if link is not None :
				sentFile = requests.get(request + '?chat_id=' + str(channel) + '&caption=' + link.replace('&', '%26'), files=telegramfile)
			else :
				sentFile = requests.get(request + '?chat_id=' + str(channel), files=telegramfile)
			if sentFile.json()['ok'] :
				sentFile = sentFile.json()
				if len(files) <= 10 :
					report = report + '`telegram...success.`'
					sendReport = True
				else :
					report = report + '`telegram...success.`'
				usedIDs.append(sentFile['result']['photo'][-1]['file_id'])
				#print('sentFile:' + str(sentFile['result']['photo'][-1]['file_id']))
				files.pop(0)
				print('success.')
			else :
				print('sentFile not ok, skipping forwards')
				print(sentFile.json())
				report = report + '`post failed.`\n`photo re-added to queue.`'
				print('failed.')
				sendReport = True
				forwardMessage = False
		else :
			print('sending file to telegram, chat_id:' + str(channel) + '...', end='')
			if link is not None :
				request = 'https://api.telegram.org/bot' + token + '/sendDocument?chat_id=' + str(channel) + '&document=' + fileToSend['file_id'] + '&caption=' + link.replace('&', '%26')
			else :
				request = 'https://api.telegram.org/bot' + token + '/sendDocument?chat_id=' + str(channel) + '&document=' + fileToSend['file_id']
			sentFile = requests.get(request)
			if sentFile.json()['ok'] :
				sentFile = sentFile.json()
				if len(files) <= 10 :
					report = report + '`telegram...success.`'
					sendReport = True
				#else :
				#	report = report + '`telegram...success.`'
				files.pop(0)
				print('success.')
			else :
				print('sentFile not ok, skipping forwards')
				print(sentFile.json())
				report = report + '`post failed.`\n`photo re-added to queue.`'
				print('failed.')
				sendReport = True
				forwardMessage = False


		# FORWARDING PHOTO
		if forwardMessage :
			print('forwarding photo to', len(forwardList), 'chats...', end='')
			successfulForwards = 0
			for i in range(len(forwardList)) :
				request = requests.get('https://api.telegram.org/bot' + token + '/forwardMessage?chat_id=' + str(forwardList[i]) + '&from_chat_id=' + str(channel) + '&message_id=' + str(sentFile['result']['message_id']))
				response = request.json()
				if response['ok'] :
					successfulForwards = successfulForwards + 1
					#print('forward[' + str(i) + '] ok')
				elif 'description' in response :
					if 'Forbidden' in response['description'] :
						removeList.append(forwardList[i])
						report = report + '\n` removed `' + str(forwardList[i]) + '` from forward list`'
						sendReport = True
					elif 'group chat was upgraded to a supergroup chat' in response['description'] and 'parameters' in response and 'migrate_to_chat_id' in response['parameters'] :
						forwardList[i] = response['parameters']['migrate_to_chat_id']
						# try again
						print('\ntrying with new ID...', end='')
						secondtry = requests.get('https://api.telegram.org/bot' + token + '/forwardMessage?chat_id=' + str(forwardList[i]) + '&from_chat_id=' + str(channel) + '&message_id=' + str(sentFile['result']['message_id']))
						if secondtry.json()['ok'] :
							successfulForwards = successfulForwards + 1
							print('success.')
						else :
							sendReport = True
							print('failed')
				else :
					getchat = requests.get('https://api.telegram.org/bot' + token + '/getChat?chat_id=' + str(forwardList[i]))
					getchat = getchat.json()
					if getchat['ok'] :
						print('\nforward[' + str(i) + '] failed (chat_id: ' + str(forwardList[i]) + ') ' + getchat['result']['title'], end='')
						report = report + '\n`forward[`' + str(i) + '`] failed (chat_id: `' + str(forwardList[i]) + '`) ` ' + getchat['result']['title']
						sendReport = True
					else :
						if 'description' in getchat :
							print('\nforward[' + str(i) + '] failed (chat_id: ' + str(forwardList[i]) + ') ' + getchat['description'], end='')
							report = report + '\n`forward[`' + str(i) + '`] failed (chat_id: `' + str(forwardList[i]) + '`) `' + getchat['description']
							if 'Forbidden' in getchat['description'] :
								removeList.append(forwardList[i])
								report = report + '\n` removed `' + str(forwardList[i]) + '` from forward list`'
								sendReport = True
						else :
							print('\nforward[' + str(i) + '] failed (chat_id: ' + str(forwardList[i]) + ')', end='')
							report = report + '\n`forward[`' + str(i) + '`] failed (chat_id: `' + str(forwardList[i]) + '`)'
							sendReport = True
					if 'description' in response :
						report = report + ' reason: `' + response['description']
					else :
						report = report + '`'
					print('\nraw response:', response, end='')
					print('\nraw command:', request.url)
			report = report + '\n` forwarded to: `' + str(successfulForwards) + '` chats`'
			print('done. ')


		# send to twitter
		if postToTwitter :
			print('sending photo to twitter...', end='')
			tries = 0
			failed = False
			while tries < 2 :
				tries = tries + 1
				try :
					if link is not None :
						status = api.PostUpdate(status=load+link, media=[snep,])
					else :
						status = api.PostUpdate(status=load, media=[snep,])
					tries = 100
					failed = False
					print('success.')
				except UnicodeDecodeError :
					print('Your message could not be encoded. Perhaps it contains non-ASCII characters?')
					print('Try explicitly specifying the encoding with the --encoding flag')
				except Exception as e : # python 3-y
					print()
					print(e)
					failed = True
					print('failed. retrying...')
				except : # python 2-y
					try :
						e = sys.exc_info()[0]
						print(e)
					except :
						print('could not load exception')
					failed = True
					print('failed. retrying...')

			if failed : # failed
				report = report + '\n`twitter...failed.`'
				sendReport = True



		
	else :
		report = report + '`post failed.`\n`no photos in queue.`\nADD PHOTOS IMMEDIATELY'
		sendReport = True
	if len(removeList) > 0 :
		for i in range(len(removeList)) :
			forwardList.remove(removeList[i])



def schedule_nextupdate():
	print()
	#reinitialize all the lists and variables as global
	global files
	global delay
	global timezone
	global report
	global scheduler
	global sendReport
	
	nextupdate = currenttime = (time.time() + ((60*60) * timezone))
	nextupdate = (nextupdate - (nextupdate % (delay * 60))) + (delay * 60)
	
	noowtime = ''
	if time.localtime(currenttime).tm_hour < 10 : noowtime = noowtime + '0'
	noowtime = noowtime + str(time.localtime(currenttime).tm_hour) + ':'
	if time.localtime(currenttime).tm_min  < 10 : noowtime = noowtime + '0'
	noowtime = noowtime + str(time.localtime(currenttime).tm_min)

	nexttime = ''
	if time.localtime(nextupdate).tm_hour < 10 : nexttime = nexttime + '0'
	nexttime = nexttime + str(time.localtime(nextupdate).tm_hour) + ':'
	if time.localtime(nextupdate).tm_min  < 10 : nexttime = nexttime + '0'
	nexttime = nexttime + str(time.localtime(nextupdate).tm_min)

	report = report + '\n`current delay: `' + str(delay) + '` minutes\ncurrent queue: `' + str(len(files)) + '`\n current time: `' + noowtime + '`\n  next update: `' + nexttime
	if len(files) < 10 :
		report = report + '\nLOW ON PHOTOS'
		sendReport = True
	#report = report + '\n`next photo in queue: `'
	
	print('current time:', noowtime)
	print(' next update:', nexttime)
	print()
	print('scheduling update for', (delay), 'minutes from now')
	#scheduler.enter((delay * 60), 1, scheduled_post, ())
	scheduler.enterabs((nextupdate - (3600 * timezone)), 1, scheduled_post, ())



def schedule_firstupdate():
	print()
	#reinitialize all the lists and variables as global
	global files
	global delay
	global timezone
	global forwardList
	global report
	global scheduler
	
	nextupdate = currenttime = (time.time() + ((60*60) * timezone))
	nextupdate = (nextupdate - (nextupdate % (delay * 60))) + (delay * 60)
	
	noowtime = ''
	if time.localtime(currenttime).tm_hour < 10 : noowtime = noowtime + '0'
	noowtime = noowtime + str(time.localtime(currenttime).tm_hour) + ':'
	if time.localtime(currenttime).tm_min  < 10 : noowtime = noowtime + '0'
	noowtime = noowtime + str(time.localtime(currenttime).tm_min)

	nexttime = ''
	if time.localtime(nextupdate).tm_hour < 10 : nexttime = nexttime + '0'
	nexttime = nexttime + str(time.localtime(nextupdate).tm_hour) + ':'
	if time.localtime(nextupdate).tm_min  < 10 : nexttime = nexttime + '0'
	nexttime = nexttime + str(time.localtime(nextupdate).tm_min)
	
	report = report + '`  bot started`\n`current delay: `' + str(delay) + '` minutes`\n`current queue: `' + str(len(files)) + '\n`     forwards: `' + str(len(forwardList)) + '\n` current time: `' + noowtime + '\n`  next update: `' + nexttime
	#report = report + '\n`next photo in queue: `'
			
	print('current time:', noowtime)
	print(' next update:', nexttime)
	print('bot started. scheduling first post...')
	print('scheduling update for', nexttime)
	#post_photo()
	scheduler.enterabs((nextupdate - (3600 * timezone)), 1, scheduled_post, ())



def get_flickr_link(filename):
	#return https://www.flickr.com/photo.gne?rb=1&id= /id/
	strings = filename.split('_')
	for i in range(len(strings)) :
		if IsInt(strings[i]) :
			return 'https://www.flickr.com/photo.gne?rb=1&id=' + strings[i]
	return None



# https://stackoverflow.com/a/1267145/8197207
def IsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False



def send_report():
	print()
	#reinitialize all the lists and variables as global
	global token
	global admins
	global files
	global report
	
	if len(files) > 0 :
		request = 'https://api.telegram.org/bot' + token + '/sendMessage'
		for i in range(len(admins)):
			request = requests.get(request + '?chat_id=' + str(admins[i]) + '&text=' + report + '&parse_mode=Markdown')
			response = request.json()
			if response['ok'] :
				print('report[' + str(i) + ']: ok')
			else :
				print('report[' + str(i) + ']: failed (' + str(admins[i]) + ')')
				if 'description' in response :
					print('reason: ' + response['description'])
				print('raw response:', response)
				print('raw request:', request.url)
	else :
		request = 'https://api.telegram.org/bot' + token + '/sendMessage'
		for i in range(len(admins)):
			requests.get(request + '?chat_id=' + str(admins[i]) + '&text=' + report + '&parse_mode=Markdown')
			requests.get(request + '?chat_id=' + str(admins[i]) + '&text=NO PHOTOS IN QUEUE&parse_mode=Markdown')
	
	print('report sent')



def initial_startup():
	print('initial_startup()')
	#reinitialize all the lists and variables as global
	global scheduler
	
	report_forwards()
	update()
	update_dropbox()
	schedule_firstupdate()
	send_report()
	
	scheduler.run()



def scheduled_post():
	print()
	#reinitialize all the lists and variables as global
	global scheduler
	global sendReport	
	
	update()
	post_photo()
	update_dropbox()
	schedule_nextupdate()
	if sendReport :
		send_report()
	sendReport = False
	scheduler.run()



initial_startup()
