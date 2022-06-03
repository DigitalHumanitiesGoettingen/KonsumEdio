from cmath import pi
from distutils import command
from re import I
import tkinter as tk

from matplotlib.image import imsave
from numpy import square
import cut_pages
from skimage.io import imread
from skimage.transform import resize
from PIL import ImageTk, Image, ImageDraw
from collections import deque
import os

def get_cuts(image, orientation,coords):
    #print(image)
    if orientation:
        lines = cut_pages.find_horizontal_line(image, 0, 0.8)
        clusters = cut_pages.find_horizontal_line_clusters(lines)
        cuts = cut_pages.find_horizontal_cuts(clusters)
        return [((cut+coords[0][0],coords[0][1]),(cut+coords[1][0], coords[1][1])) for cut in cuts]
    else:
        lines = cut_pages.find_vertical_line(image, 0, 0.8)
        clusters = cut_pages.find_vertical_line_clusters(lines)
        cuts = cut_pages.find_vertical_cuts(clusters)
        return [((coords[0][0], cut+coords[0][1]),(coords[2][0], cut+coords[2][1])) for cut in cuts]

def draw_cuts(image, cuts):
    draw = ImageDraw.Draw(image)
    for cut in cuts:
        draw.line(cut, fill="Red", width = 10)
        
def square_size(coords):
    
    len_x = abs(coords[1][1] - coords[0][1])
    print("len_x: " , len_x)
    len_y = abs(coords[2][0] - coords[0][0])
    print("len_y: ", len_y)
    return len_x*len_y


def slicing(image, depth):
    print(image.shape)
    coordinates = deque()
    cuts = []
    dq = deque()
    max_depth = depth
    dq.append(((0,0), (0,image.shape[1]), (image.shape[0], 0), (image.shape[0], image.shape[1]),0))
    coordinates.append(((0,0), (0,image.shape[1]), (image.shape[0], 0), (image.shape[0], image.shape[1]),0))
    orientation = True # True = horizontal, False = vertical
    last_depth = 0

    while dq:
        coords = dq.popleft()
        coordinates.popleft()
        spare_coordinates = []
        #print("coords: ",coords)
        depth = coords[4]
        if depth == max_depth: 
            spare_coordinates.append(coords)
            break
        if depth > last_depth:
            orientation = not orientation
        last_depth = depth
        depth += 1
        #print(image[39:44][28:1263].shape)
        new_cuts = get_cuts(image[coords[0][0]:coords[2][0]+1,coords[0][1]:coords[1][1]+1],orientation,coords)
        #print("new coords: ", new_coords)
        #print("Square size: ", square_size(coords))
        if not new_cuts: 
            #print("hoi")
            spare_coordinates.append(coords)
            continue
        last_cut = None

       
        for i in range(len(new_cuts)):
            new_cut = new_cuts[i]
            #print(new_cut)
            if last_cut == None:
                if orientation:
                    #print("hf",coords[0],coords[1],new_cut[0],new_cut[1])
                    new_coords = (coords[0],coords[1],new_cut[0],new_cut[1],depth)
                    dq.append(new_coords)
                    coordinates.append(new_coords)
                else:
                    #print("vf",coords[0],new_cut[0],coords[2],new_cut[1])
                    new_coords = (coords[0],new_cut[0],coords[2],new_cut[1],depth)
                    dq.append(new_coords)
                    coordinates.append(new_coords)
            else:
                if orientation:
                    #print("h",last_cut[0],last_cut[1], new_cut[0], new_cut[1])
                    new_coords = (last_cut[0],last_cut[1], new_cut[0], new_cut[1],depth)
                    dq.append(new_coords)
                    coordinates.append(new_coords)
                else:
                    #print("v",last_cut[0],new_cut[0],last_cut[1],new_cut[1])
                    new_coords = (last_cut[0],new_cut[0],last_cut[1],new_cut[1],depth)
                    dq.append(new_coords)
                    coordinates.append(new_coords)
            if orientation:
                last_cut = ((new_cut[0][0]+1,new_cut[0][1]),(new_cut[1][0]+1,new_cut[1][1]))
            else:
                last_cut = ((new_cut[0][0],new_cut[0][1]+1),(new_cut[1][0],new_cut[1][1]+1))
                
            cuts.append(new_cut)
        if orientation:
            #print("hl",last_cut[0],last_cut[1],coords[2],coords[3])
            dq.append((last_cut[0],last_cut[1],coords[2],coords[3],depth))
        else:
            #print("vl",last_cut[0],coords[1],last_cut[1],coords[3])
            dq.append((last_cut[0],coords[1],last_cut[1],coords[3],depth))
        

   
    spare_coordinates.append(coords)
    for element in spare_coordinates:
        coordinates.append(element)
    print("number of boxes: ", len(coordinates))
    return cuts, coordinates

def make_picture(path, depth):
    global current_cuts
    image = Image.open(path).convert("RGB")
    sciki_image = imread(path)
    cuts, coordinates = slicing(sciki_image, depth)
    #print(coordinates)
    current_cuts = cuts
    pil_cuts = [((cut[0][1],cut[0][0]),(cut[1][1],cut[1][0]))for cut in cuts]
    draw_cuts(image, pil_cuts)
    return image, cuts, coordinates

def on_decrease_depth_button():
    global depth, depth_label, path, filelist, photo, i, img, g_coordinates
    depth -= 1
    depth_label.configure(text=str(depth))
    img, cuts, coordinates = make_picture(path+"/"+filelist[i], depth)
    g_coordinates = coordinates
    img = img.resize((img.width//6 ,img.height//6), Image.ANTIALIAS)
    photo = ImageTk.PhotoImage(img)
    canvas.itemconfig(image_container, image=photo)

def on_increase_depth_button():
    global depth, depth_label, path, filelist, photo, i, img, g_coordinates
    depth += 1
    depth_label.configure(text=str(depth))
    img, cuts, coordinates = make_picture(path+"/"+filelist[i], depth)
    g_coordinates = coordinates
    img = img.resize((img.width//6 ,img.height//6), Image.ANTIALIAS)
    photo = ImageTk.PhotoImage(img)
    canvas.itemconfig(image_container, image=photo)

def on_next_button():
    global i, depth, photo, path, filelist, img, g_coordinates
    i += 1
    img, cuts, coordinates = make_picture(path+"/"+filelist[i], depth)
    g_coordinates = coordinates
    img = img.resize((img.width//6 ,img.height//6), Image.ANTIALIAS)
    photo = ImageTk.PhotoImage(img)
    canvas.itemconfig(image_container, image=photo)

def on_save_button():
    global out_path, g_coordinates, in_path
    i = 0
    img = imread(in_path)
    try:
        os.mkdir(out_path)
    except: 
        for imname in os.listdir(out_path):
            os.remove(out_path+"/"+imname)
    for coord in g_coordinates:
        image = slice(coord, img)
        imsave(out_path + str(i) + ".png", image)
        i += 1

def slice(coords, image):
    return image[coords[0][0]:coords[2][0]+1,coords[0][1]:coords[1][1]+1]

def is_in_box(x, y, box):
    #print(x, y)
    #print(box)
    if(y >= box[0][0] and y <= box[2][0] and x >= box[0][1] and x <= box[1][1]):
        print(x, y, "Is in box ", box)
        return True
    else:
        return False

def click_on_canvas(event):
    print("mouse_clicked at x: ", event.x, " y: ", event.y)
    global o, img, draw, resized_img, current_cuts, g_coordinates
    x = event.x
    y = event.y
    line = None
    if o.get() == "h":
        for box in g_coordinates:
            #print(box)
            if is_in_box(x*6, y*6, box):
                line = (box[0][1]//6, y, box[1][1]//6, y)
                #print("box coords: ", box[0][1]//6, box[1][1]//6)
                #print(line)
                canvas.create_line(line, fill="blue", width = 2)
                break
            else:
                print(x*6, y*6,"Is not in box", box)
       
     
    elif o.get() == "v":
        line = (event.y, 0, event.y, resized_img.height)
        canvas.create_line(line, fill="blue", width=2)

def get_coords(cuts, image):
    
    coords = []
    cuts.sort(key=lambda x: x[0][0])
    
    

    




path = "../input/prep/bin"

filelist = os.listdir(path)
depth = 3
i = 0
current_cuts = None
in_path = "../input/raw/" + filelist[i][:-4] + ".jpg"
out_path = "../output_int/" + filelist[i][:-4] + "/"
img, cuts, g_coordinates = make_picture(path+"/"+filelist[i], depth)
get_coords(cuts, Image.open(path+"/"+filelist[i]).convert('RGB'))
resized_img = img.resize((img.width//6 ,img.height//6), Image.ANTIALIAS)
draw = ImageDraw.Draw(img)
window = tk.Tk()
o = tk.StringVar(window)
depth_label = tk.Label(window, text=str(depth))
canvas = tk.Canvas(window, width=resized_img.width, height=resized_img.height)
label = tk.Label(
    text="Interaktive Layout-Analyse",
    width = 50,
    height = 5)
label.pack()

decrease_depth_button = tk.Button(window, text="-", command=on_decrease_depth_button).pack(side="left")
depth_label.pack(side="left")
increase_depth_button = tk.Button(window, text="+", command=on_increase_depth_button).pack(side="left")

v_radio = tk.Radiobutton(window, text="v", variable=o, value="v").pack(side="right")
h_radio = tk.Radiobutton(window, text="h", variable=o, value="h").pack(side="right")
del_radio = tk.Radiobutton(window, text="del", variable=o, value="del").pack(side="right")
canvas.pack()
canvas.bind("<Button>", click_on_canvas)
photo = ImageTk.PhotoImage(resized_img)
image_container = canvas.create_image(0,0,anchor=tk.NW, image=photo)
next_button=tk.Button(window, text="Weiter", command=on_next_button).pack()
save_button=tk.Button(window, text="Speichern", command=on_save_button).pack()


tk.mainloop()



