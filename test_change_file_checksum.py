import pickle
#import md5
from shutil import copyfile

# def check_for changes(file1,file2):

	
# 	hash1 = md5.new()
# 	hash1.update(file1)
# 	hash1.digest() # this generates the checksum

# 	hash2 = md5.new()
# 	hash1.update(file2)
# 	hash2.digest() # this generates the checksum




def equalsFile_old(firstFile, secondFile, blocksize=65536):
    buf1 = firstFile.read(blocksize)
    buf2 = secondFile.read(blocksize)
    while len(buf1) > 0:
        if buf1!=buf2:
            return False
        buf1, buf2 = firstFile.read(blocksize), secondFile.read(blocksize)
    return True
# =============================================================================
def equalsFile(firstFile, secondFile, blocksize=65536):
    #returns True if files are the same,i.e. secondFile has same checksum as first
    if os.path.getsize(firstFile) != os.path.getsize(secondFile):
        return False
    else:
        firstFile = open(firstFile , 'rb')
        secondFile =  open(secondFile  , 'rb')
        buf1 = firstFile.read(blocksize)
        buf2 = secondFile.read(blocksize)
        while len(buf1) > 0:
            if buf1!=buf2:
                return False
            buf1, buf2 = firstFile.read(blocksize), secondFile.read(blocksize)
    return True
# 
# =============================================================================
def copy_changed_kg1_to_save(src,dst,filename):
    """
    src: is the 
    """
    
    src='./'+src+'/'+filename
    dst='./'+dst+'/'+filename
    
    copyfile(src, dst)

    #%%
#%



#%%


#if __name__ == '__main__':
val_seq =100
with open('./saved/untitled.pkl', 'wb') as f:
    pickle.dump(val_seq,f)
f.close()
#%    
#%%
copy_changed_kg1_to_save('saved','scratch','untitled.pkl')
  #%%
with open('./saved/untitled.pkl','rb') as f:
    val_seq = pickle.load(f)
f.close()

#%%
val_seq_original = val_seq
val_seq =1
test = 1213
with open('./scratch/untitled.pkl', 'wb') as f:
    pickle.dump([val_seq,test],f)
f.close()
#%%
import os
# if os.path.getsize('./saved/untitled.pkl') != os.path.getsize('./scratch/untitled.pkl',):
    # print('detected size change! data changed')
# else:
    # data_changed = equalsFile(open('./saved/untitled.pkl', 'rb'), open('./scratch/untitled.pkl', 'rb'))
data_changed = equalsFile('./saved/untitled.pkl', './scratch/untitled.pkl')

#%%

if not data_changed:
#    print('no changes detected')
    print('data changed')
else:
    print('no changes detected')
    
#    print('data changed')
        
