#!/usr/bin/env python
"""

"""
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from apiclient.http import MediaFileUpload
from pprint import pprint
import sys

def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")

class appDataFolder:
	def __init__(
			self,
			scopes = 'https://www.googleapis.com/auth/drive.appfolder https://www.googleapis.com/auth/drive.appdata https://www.googleapis.com/auth/drive https://www.googleapis.com/auth/drive.file',
			credentials = 'credentials.json',
			client_secret = 'client_secret.json'
		):
		self.scopes = scopes;
		self.credentials = credentials;
		store = file.Storage(self.credentials)
		creds = store.get()
		if not creds or creds.invalid:
			flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
			creds = tools.run_flow(flow, store)
		self.service = build('drive', 'v3', http=creds.authorize(Http()))
		
	def interactive_list(self):
		res = self.service.files().list(
				spaces='appDataFolder',
				fields='nextPageToken, files(id, name)'
			).execute()
			
		files = res.get('files', [])
		if not files:
		    print('No files found.')
		else:
		    print('Files:')
		    for f in files:
		        print('{0} ({1})'.format(f['name'], f['id']))
		        pprint(f)
		        
	def list(self):
		res = self.service.files().list(
				spaces='appDataFolder',
				fields='nextPageToken, files(id, name)'
			).execute()
		myList = []	
		files = res.get('files', [])
		for f in files:
			myList.append(f['id'])
		return(myList)
		        
	def delete( self, id):
		self.service.files().delete(fileId=id).execute()
		
	def interactive_delete(self):
		for id in self.list():
			pprint(id)
			meta = self.service.files().get(fileId=id).execute()
			print("\n\n")
			pprint(meta)
			ans = query_yes_no('Do you want to delete this file?', default="yes")
			if ans:
				self.delete(id)

	def __get_meta(self,id):
		meta = self.service.files().get(fileId=id).execute()
		return(meta)
	
	def __get_file_name(self,id):
		return(self.__get_meta(id)['name'])

	def find(self,
			file_name = ''
		):
		ids=[]
		for id in self.list():
			name = self.__get_file_name(id)
			if name == file_name:
				ids.append(id)
		if len(ids)==0:
			return(None)
		if len(ids) > 1:
			print("WARNING: More than one file with name %s was found." % file_name)
		return(ids[0])

	def upload(self,
			file_name = '',
			file_path = '.'
		):
		id = self.find(file_name=file_name)
		media = MediaFileUpload(
			file_path+'/'+file_name,
			#mimetype='application/vnd.google-apps.file',
			mimetype='application/json',
			resumable=True )
		if id is None:
			file_metadata = {
	    		'title': file_name,
	    		'name' : file_name,
	    		'parents': ['appDataFolder'] }
			file = self.service.files().create(
					body=file_metadata,
					media_body=media,
					fields='id'
				).execute()
		else:
			file_metadata = {
	    		'title': file_name,
	    		'name' : file_name }
			file = self.service.files().update(
					fileId=id,
					body=file_metadata,
					media_body=media,
					fields='id'
				).execute()
		return(file)

if __name__ == "__main__":
	pass

