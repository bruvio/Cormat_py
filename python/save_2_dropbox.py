
import dropbox
from dropbox import DropboxOAuth2FlowNoRedirect
import pathlib
import re
import os
import six
from numpy import arange
'''
This example walks through a basic oauth flow using the existing long-lived token type
Populate your app key and app secret in order to run this locally
'''
def upload_to_dropbox(pulselist,inputfolder):
    # APP_KEY = "b5tkict7tmtq7ig"
    # APP_SECRET = "baaiqhm6bcjskn7"
    # # the source folder
    folder = os.getcwd()+"/"+inputfolder    # located in this folder
    #
    #
    #
    # auth_flow = DropboxOAuth2FlowNoRedirect(APP_KEY, APP_SECRET)
    # #
    # authorize_url = auth_flow.start()
    # print("1. Go to: " + authorize_url)
    # print("2. Click \"Allow\" (you might have to log in first).")
    # print("3. Copy the authorization code.")
    # auth_code = input("Enter the authorization code here: ").strip()
    # try:
    #     oauth_result = auth_flow.finish(auth_code)
    # except Exception as e:
    #     print('Error: %s' % (e,))
    #     exit(1)

    # with dropbox.Dropbox(oauth2_access_token=oauth_result.access_token) as dbx:
    with dropbox.Dropbox(
                oauth2_access_token='v1LUCAfjVFAAAAAAAAGr06If8oO8KPaJchZB6uxTlHERA_N8wxJNjq0Q9sXogWCE') as dbx:
        dbx.users_get_current_account()
        for root, dirs, files in os.walk(folder):
            for folders in dirs:
                if folders.isdigit():
                    if int(folders) in pulselist:
                        for dd,aa,files in os.walk(folder+os.sep+folders):
                            for file in files:
                                full_file_name = os.path.join(folder, folders,file)
                                fullfilename = pathlib.Path(full_file_name)
                                targetfile = os.sep+folders+os.sep+file
                                print('uploading {}\n'.format(targetfile))
                                with fullfilename.open("rb") as f:
                                    meta = dbx.files_upload(f.read(), targetfile, mode=dropbox.files.WriteMode("overwrite"))
        #                         # create a shared link
        #                         link = dbx.sharing_create_shared_link(targetfile)
        #
        #                         # url which can be shared
        #                         url = link.url
        #
        #                         # link which directly downloads by replacing ?dl=0 with ?dl=1
        #                         dl_url = re.sub(r"\?dl\=0", "?dl=1", url)
        #                         print(dl_url)

        fullfilename = pathlib.Path('./pulselist.txt')
        if os.path.isfile(fullfilename):
            targetfile = os.sep +  'pulselist.txt'
            with fullfilename.open("rb") as f:
                meta = dbx.files_upload(f.read(), targetfile,
                                    mode=dropbox.files.WriteMode("overwrite"))

def download_from_dropbox(pulselist,folder):
    # APP_KEY = "b5tkict7tmtq7ig"
    # APP_SECRET = "baaiqhm6bcjskn7"
    #
    #
    # auth_flow = DropboxOAuth2FlowNoRedirect(APP_KEY, APP_SECRET)
    # #
    # authorize_url = auth_flow.start()
    # print("1. Go to: " + authorize_url)
    # print("2. Click \"Allow\" (you might have to log in first).")
    # print("3. Copy the authorization code.")
    # auth_code = input("Enter the authorization code here: ").strip()
    # try:
    #     oauth_result = auth_flow.finish(auth_code)
    # except Exception as e:
    #     print('Error: %s' % (e,))
    #     exit(1)

    # with dropbox.Dropbox(oauth2_access_token=oauth_result.access_token) as dbx:
    with dropbox.Dropbox(oauth2_access_token='v1LUCAfjVFAAAAAAAAGr06If8oO8KPaJchZB6uxTlHERA_N8wxJNjq0Q9sXogWCE') as dbx:
        dbx.users_get_current_account()
        response = dbx.files_list_folder(path="")
        print(response)
        for ii in range(0,len(response.entries)):
            if response.entries[ii].name.isdigit():
                if int(response.entries[ii].name) in pulselist:
                    print(response.entries[ii].name)
                    pathlib.Path(
                        './'+folder + os.sep + str(response.entries[ii].name) ).mkdir(
                        parents=True,
                        exist_ok=True)
                    entries = dbx.files_list_folder(path=response.entries[ii].path_lower)
                    # md, res = dbx.files_download_to_file(folder+os.sep+str(response.entries[ii].name),response.entries[ii].path_lower)
                    for entry in entries.entries:
                        print('downloading {}\n'.format(str(response.entries[ii].name+os.sep+entry.name)))
                        dbx.files_download_to_file(path=entry.path_lower,download_path=os.getcwd()+os.sep+folder+os.sep+str(response.entries[ii].name+os.sep+entry.name))



if __name__ == "__main__":
    pulselist =[97514,
97515,
97516,
97517,
97518,
97521,
97522,
97523,
97524,
97525,
97527,
97528]
    pulselist = list(arange(97560,97563))
    pulselist = [97512,
                 97509,
                 97510,
                 97511]
    # upload_to_dropbox(pulselist,'scratch')
    download_from_dropbox(pulselist,'saved')
    # download_from_dropbox([97133],'scratch')
