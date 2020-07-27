
import dropbox
from dropbox import DropboxOAuth2FlowNoRedirect
import pathlib
import re
import os


'''
This example walks through a basic oauth flow using the existing long-lived token type
Populate your app key and app secret in order to run this locally
'''
def upload_to_dropbox(pulselist):
    APP_KEY = "b5tkict7tmtq7ig"
    APP_SECRET = "baaiqhm6bcjskn7"
    # the source folder
    folder = os.getcwd()+"/scratch"    # located in this folder



    auth_flow = DropboxOAuth2FlowNoRedirect(APP_KEY, APP_SECRET)
    #
    authorize_url = auth_flow.start()
    print("1. Go to: " + authorize_url)
    print("2. Click \"Allow\" (you might have to log in first).")
    print("3. Copy the authorization code.")
    auth_code = input("Enter the authorization code here: ").strip()
    try:
        oauth_result = auth_flow.finish(auth_code)
    except Exception as e:
        print('Error: %s' % (e,))
        exit(1)


    with dropbox.Dropbox(oauth2_access_token=oauth_result.access_token) as dbx:
        dbx.users_get_current_account()
        for root, dirs, files in os.walk(folder):
            for folders in dirs:
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
        targetfile = os.sep +  'pulselist.txt'
        with fullfilename.open("rb") as f:
            meta = dbx.files_upload(f.read(), targetfile,
                                mode=dropbox.files.WriteMode("overwrite"))


if __name__ == "__main__":
    upload_to_dropbox([])