import os
import shutil
from tqdm import tqdm

path="/home/jakob/Johanna/Masterarbeit/corpus/Jugend/Jahrgang 2/PNG"
out_path="/home/jakob/Johanna/Masterarbeit/corpus/Jugend/Jahrgang 2/all"

dirlist = os.listdir(path)
k = 0
for i in tqdm(range(0, len(dirlist))):
    filelist = os.listdir(path+"/"+dirlist[i])
    for j in range(0, len(filelist)):
        shutil.copyfile(path+"/"+dirlist[i]+"/"+filelist[j], out_path+"/"+str(k)+".jpg")
        k += 1