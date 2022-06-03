import os
from pdf2image import convert_from_path


in_path = "../corpus/Berliner Volkszeitung/1918"
out_path = "../corpus/Berliner Volkszeitung/1918/PNG"

for filename in os.listdir(in_path):
    try:
        os.mkdir(out_path+"/"+filename[:-4])
    except:
        print("Folder", filename[:-4], " already exists")

    images = convert_from_path(in_path+"/"+filename)
    
    for i in range(len(images)):

        images[i].save(out_path+'/'+filename[:-4]+'/'+ str(i) +'.jpg', 'JPEG')
    