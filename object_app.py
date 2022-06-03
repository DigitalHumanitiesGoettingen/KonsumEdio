from cmath import pi
from datetime import date
from distutils import command
from hashlib import new
from re import I
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from typing import Deque

from matplotlib.image import imsave
import numpy
import cut_pages
from skimage.io import imread
from skimage.transform import resize
from PIL import ImageTk, Image, ImageDraw
from collections import deque
import os
import json
from Box import Box

def get_cuts(image, orientation):
    #print(image)
    if orientation:
        lines = cut_pages.find_horizontal_line(image, 0, 0.8)
        clusters = cut_pages.find_horizontal_line_clusters(lines)
        cuts = cut_pages.find_horizontal_cuts(clusters)
        return [(cut, orientation) for cut in cuts]
    else:
        lines = cut_pages.find_vertical_line(image, 0, 0.8)
        clusters = cut_pages.find_vertical_line_clusters(lines)
        cuts = cut_pages.find_vertical_cuts(clusters)
        return [(cut, orientation) for cut in cuts]

def split(image, max_depth):
    # Initialize deque
    dq = deque()
    init_box = Box((0, 0), (image.width, 0), (0, image.height), (image.width, image.height), 0)
    dq.append(init_box)
    #init_box.to_print()
    orientation = True
    last_depth = 0

    while dq:
        
        current_box = dq.popleft()
        print(" ************ New current box **********")
        current_box.to_print()
        depth = current_box.depth
        
        
        # Check if target depth is reached
        print("********* Check depth **********")
        print("depth: ", depth)
        print("last depth: ", last_depth)
        if(depth == max_depth):
            dq.append(current_box)
            break
        if(depth > last_depth):
            print("changing orientation to ", (not orientation))
            orientation = not orientation
        last_depth = depth
        #print("orientation: ", orientation)
        # Get cuts for current box
        print("********** Get new cuts **********")
        
        new_cuts = get_cuts(current_box.fit_image(image), orientation)
        new_cuts.sort(key=lambda x:x[0])
        print(new_cuts)
        if not new_cuts:
            dq.append(current_box)
            continue

        # Skip if box is too small
        #print("********** Check size *********")
        #print(current_box.size)
        #if orientation and current_box.height < 500:
        #    print("Too small. Skip.")
        #    dq.append(current_box)
        #    continue

        #if not orientation and current_box.width < 500:
        #    print("Too small. Skip.")
        #    dq.append(current_box)
        #    continue

        print("********* Splitting **********")
        for i in range(len(new_cuts)):
            print("Split at ", new_cuts[i])
            new_cut = new_cuts[i]
            old_box = Box(current_box.top_left, current_box.top_right, current_box.bottom_left, current_box.bottom_right, current_box.depth)
            new_box = current_box.split(new_cut[0], new_cut[1])
            print("********** Checking size **********")
            if(not new_box):
                print("========= New Box too small, using old one ========")
                current_box = old_box
                current_box.to_print()

            elif(new_box.width < 200 or new_box.height < 200 or current_box.width < 200 or current_box.height < 200):
                print("========== Scrapping new box, current box: =========")
                current_box = old_box
                current_box.to_print()
            else:
                print("========== Appending new box =========")
                dq.append(new_box)

        
        current_box.depth += 1
        print("********* Appending current box *********")
        current_box.to_print()
        dq.append(current_box)
        #print("deque: ============")
        #for i in range(len(dq)):
        #    dq[i].to_print()
        #print("======================")
             
            
    return(dq)
            
def draw_boxes(image, boxes):
    global factor
    draw = ImageDraw.Draw(image)
    print("========== Drawing Boxes =========")
    print("Line width: " + str(factor+2))
    for box in boxes:
        box.to_print()
        if box.contains_ad:
            draw.rectangle([(box.top_left[0], box.top_left[1]), (box.bottom_right[0], box.bottom_left[1])], outline="Red", width=5)
        else:
            draw.rectangle([(box.top_left[0], box.top_left[1]), (box.bottom_right[0], box.bottom_left[1])], outline="Red", width=5, fill="Black")

def set_factor(width):
    if width//524 <= 1:
        return 2
    else: return width//524

def make_picture(path, depth):
    global factor
    image = Image.open(path)
    rgb_image = Image.open(path).convert('RGB')
    boxes = split(image, depth)
    draw_boxes(rgb_image, boxes)
    print(image.width, image.height)
    factor = set_factor(image.width)
    image = rgb_image.resize((image.width//factor, image.height//factor), Image.ANTIALIAS)
    return image, boxes

def on_next_button(*event):
    global i, image, path, filelist, depth, boxes, photo, in_path
    i += 1
    in_path = path+"/"+filelist[i]
    image, boxes = make_picture(in_path, depth)
    photo = ImageTk.PhotoImage(image)
    canvas.itemconfig(image_container, image=photo)

def on_decrease_depth_button():
    global depth, depth_label, path, filelist, i, photo, boxes
    depth -= 1
    depth_label.configure(text=str(depth))
    image, boxes = make_picture(path + "/"+filelist[i], depth)
    photo = ImageTk.PhotoImage(image)
    canvas.itemconfig(image_container, image=photo)

def on_increase_depth_button():
    global depth, depth_label, path, filelist, i, photo, boxes
    depth += 1
    depth_label.configure(text=str(depth))
    image, boxes = make_picture(path + "/"+filelist[i], depth)
    photo = ImageTk.PhotoImage(image)
    canvas.itemconfig(image_container, image=photo)

def on_save_button(*event):
    global  path, filelist, i, boxes, metadata, out_path
    j = 0
    big_image = Image.open(path + "/"+filelist[i])
    try:
        os.mkdir(out_path+"/"+filelist[i][:-4])
    except:
        for imname in os.listdir(out_path+"/"+filelist[i][:-4]):
            os.remove(out_path+"/"+imname)
    for box in boxes:
        if not box.contains_ad:
            continue
        image = box.fit_image(big_image)
        imarr = numpy.asarray(image)
        imarr = imarr*255
        #print(imarr)
        #print(image.shape)
        image.save(out_path+"/"+filelist[i][:-4]+"/" + str(j) + ".jpeg", 'jpeg')
        print("Saving to ", out_path+"/"+filelist[i][:-4]+"/" + str(j) + ".json")
        metadata["File"] = str(j) + ".jpeg"
        metadata["Size"] = box.size
        metadata["Box"] = json.dumps(box.to_dict())
        metadata["Percent_page"] = percentage_of_page(box)
        with open(out_path+"/"+filelist[i][:-4]+"/" + str(j) + ".json", 'w') as file:
            file.write(json.dumps(metadata))
        #imsave(out_path + str(j) + ".png", imarr)
        j += 1
    with open(out_path+"/"+filelist[i][:-4]+"/"+"page_meta.json", 'w') as file:
        file.write("[")
        for box in boxes:
            file.write(json.dumps(box.to_dict()) + ",\n")
        file.write("]")


def click_on_canvas(event):
    print("mouse_clicked at x: ", event.x, " y: ", event.y)
    global boxes, filename, i, o, path, photo, wait, b1, b2, image, factor
    print(o.get())
    x = event.x
    y = event.y
    if o.get() == "h":
        n_boxes = len(boxes)
        print("Boxes before split: ", n_boxes)
        for j in range(0, n_boxes):
            print("========== Current Box ==========")
            box = boxes.popleft()
            box.to_print()
            if box.is_in_box(x*factor, y*factor):
                print("---------- Click is in Box ----------")
                new_box = box.split(y*factor, True)
                print("new box")
                new_box.to_print()
                print("box")
                box.to_print()
                boxes.append(new_box)
                boxes.append(box)
                break
            else:
                print("--------- Click not in box, reappending ---------")
                boxes.append(box)
                j += 1
        image = Image.open(path+"/"+filelist[i]).convert('RGB')
        factor =set_factor(image.width)
        print(image.width, image.height)
        draw_boxes(image, boxes)
        image = image.resize((image.width//factor, image.height//factor), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(image)
        canvas.itemconfig(image_container, image=photo)

    if o.get() == "v":
        n_boxes = len(boxes)
        print("Boxes before split: ", n_boxes)
        for j in range(0, n_boxes):
            print("========== Current Box ==========")
            box = boxes.popleft()
            box.to_print()
            if box.is_in_box(x*factor, y*factor):
                print("---------- Click is in Box ----------")
                new_box = box.split(x*factor, False)
                print("new box")
                new_box.to_print()
                print("box")
                box.to_print()
                boxes.append(new_box)
                boxes.append(box)
                break
            else:
                print("--------- Click not in box, reappending ---------")
                boxes.append(box)
                j += 1
        image = Image.open(path + "/" + filelist[i]).convert('RGB')
        factor = set_factor(image.width)
        print(image.width, image.height)
        draw_boxes(image, boxes)
        image = image.resize((image.width//factor, image.height//factor), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(image)
        canvas.itemconfig(image_container, image=photo)

    if o.get() == "m":
        wait = not wait
        print("wait: ", wait)
        n_boxes = len(boxes)
        if wait:
            print("--------- Waiting for second click ----------")
            for k in range(0, n_boxes):
                box = boxes.popleft()
                if(box.is_in_box(x*factor, y*factor)):
                    print("Found matching box")
                    b1 = Box(box.top_left, box.top_right, box.bottom_left, box.bottom_right, depth)
                    break
                boxes.append(box)
        if not wait:
            print("----------- Received second click ---------")
            for k in range(0, n_boxes):
                box = boxes.popleft()
                if(box.is_in_box(x*factor,y*factor)):
                    b2 = Box(box.top_left, box.top_right, box.bottom_left, box.bottom_right, depth)
                    b1.merge(b2)
                    boxes.append(b1)
                    break
                boxes.append(box)
        
        image = Image.open(path+"/"+filelist[i]).convert('RGB')
        factor = set_factor(image.width)
        print(image.width, image.height)
        draw_boxes(image, boxes)
        image = image.resize((image.width//factor, image.height//factor), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(image)
        canvas.itemconfig(image_container, image=photo)

    if o.get() == "i":
        for box in boxes:
            if(box.is_in_box(x*factor, y*factor)):
                box.contains_ad = False

        image = Image.open(path+"/"+filelist[i]).convert('RGB')
        factor = set_factor(image.width)
        print(image.width, image.height)
        draw_boxes(image, boxes)
        image = image.resize((image.width//factor, image.height//factor), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(image)
        canvas.itemconfig(image_container, image=photo)
                


def on_key(event):
    if(event.keysym =="v"):
        o.set("v")
    if(event.keysym == "h"):
        o.set("h")
    if(event.keysym == "m"):
        o.set("m")
    if(event.keysym == "i"):
        o.set("i")
    
def on_define_metadata():

    meta_window = tk.Toplevel()
    meta_window.wm_title("Metadata")
    magazine_label = tk.Label(meta_window, text="Magazine: ").pack()
    magazine_input = tk.Entry(meta_window, textvariable=magazine, width=20).pack()
    issue_label = tk.Label(meta_window, text="Issue: ").pack()
    issue_input = tk.Entry(meta_window, textvariable=issue, width=20).pack()
    date_label = tk.Label(meta_window, text="Date: ").pack()
    date_input = tk.Entry(meta_window, textvariable=p_date, width=20).pack()
    page_label = tk.Label(meta_window, text="Page: ").pack()
    page_input = tk.Entry(meta_window, textvariable=page, width=20).pack()
    save_metadata_button = ttk.Button(meta_window, text="Save Metadata", command=on_save_metadata).pack()

def on_save_metadata():
    global metadata
    metadata['Magazine'] = magazine.get()
    metadata['Issue'] = issue.get()
    metadata['Date'] = p_date.get()
    metadata['Page'] = page.get()
    
def percentage_of_page(box):
    global image, factor
    imsize = image.height*factor*image.width*factor
    print("Imsize ", imsize, " = ", image.height, " * ", image.width)
    boxsize = box.size[0]*box.size[1]
    print("Boxsize ", boxsize)
    return boxsize/imsize

def on_set_paths_button():

    path_window = tk.Toplevel()
    path_window.wm_title("Pfade angeben")
    tk.Button(path_window, text="Input-Pfad", command=set_input_path).pack()
    tk.Button(path_window, text="Output-Pfad", command=set_output_path).pack()

def set_input_path():
    global path, image, boxes, i, depth, filelist, photo
    path  = filedialog.askdirectory()
    filelist = os.listdir(path)
    i = 0
    print(path + "/" +filelist[i])
    image, boxes = make_picture(path + "/" +filelist[i], depth)
    photo = ImageTk.PhotoImage(image)
    canvas.itemconfig(image_container, image=photo)

def set_output_path():
    global out_path
    out_path  = filedialog.askdirectory() + "/"




##### APPLICATION #####
path = "../input/prep/bin"
filelist = os.listdir(path)
depth = 2
i = 0
boxes = []
wait = False
b1 = None
b2 = None
metadata = {}



## Load image and setup draw
image = Image.open(path + "/"+filelist[i])
rgb_image = Image.open(path+"/"+filelist[i]).convert('RGB')
out_path = "../output_int/" + filelist[i][:-4] + "/"
draw = ImageDraw.Draw(image)
in_path = path + "/"+filelist[i]
factor = set_factor(image.width)
window = tk.Tk()
s = ttk.Style()
s.theme_use('clam')
o = tk.StringVar(window)
magazine = tk.StringVar()
issue = tk.StringVar()
p_date = tk.StringVar()
page = tk.StringVar()
depth_label = tk.Label(window, text=str(depth))
canvas = tk.Canvas(window, width=image.width//factor, height=image.height//factor)
label = tk.Label(
    text="Interaktive Layout-Analyse",
    width = 50,
    height = 5)
label.pack()

decrease_depth_button = ttk.Button(window, text="-", command=on_decrease_depth_button).pack(side="left")
depth_label.pack(side="left")
increase_depth_button = ttk.Button(window, text="+", command=on_increase_depth_button).pack(side="left")

v_radio = ttk.Radiobutton(window, text="v", variable=o, value="v").pack(side="right")
h_radio = ttk.Radiobutton(window, text="h", variable=o, value="h").pack(side="right")
del_radio = ttk.Radiobutton(window, text="m", variable=o, value="m").pack(side="right")
i_radio = ttk.Radiobutton(window, text="i", variable=o, value="i").pack(side="right")

boxes = split(image, depth)
draw_boxes(rgb_image, boxes)
image = rgb_image.resize((image.width//factor, image.height//factor), Image.ANTIALIAS)
print(image.width, image.height)
photo = ImageTk.PhotoImage(image)


canvas.pack()
canvas.bind("<Button>", click_on_canvas)
window.bind("<Key>", on_key)
window.bind("<space>", on_save_button)
window.bind("<Right>", on_next_button)

image_container = canvas.create_image(0,0,anchor=tk.NW, image=photo)
next_button=ttk.Button(window, text="Weiter", command=on_next_button).pack()
save_button=ttk.Button(window, text="Speichern", command=on_save_button).pack()
metadata_button=ttk.Button(window, text="Define Metadata", command=on_define_metadata).pack()
set_paths_button=ttk.Button(window, text="Dateipfade", command=on_set_paths_button).pack()

tk.mainloop()
