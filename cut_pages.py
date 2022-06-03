# %% [markdown]
# # Bilder zerschneiden
# 
# Diese Routine zerschneidet Seiten mit Anzeigen in einzelne Bilder, die jeweils eine Anzeige erhalten.
# 
# ## Vorraussetzungen
# - Im Ordner ``../input/prep/bin`` liegen binäre Varianten der Seiten, die zerschnitten werden sollen.
#     - Dafür kann das Notebook ``prep_images.ipynb`` verwendet werden.
# 
# ## Ergebnis
# - Im Ordner ``../output`` liegt für jede Seite jeweils ein Ordner, der alle auf dieser Seite enthaltenen Anzeigen als einzelne Bilder enthält

# %% [markdown]
# ### Imports

# %%
from skimage.io import imread, imsave
from skimage.draw import line
import os
import shutil
from PIL import Image
import numpy


# %% [markdown]
# ### Definitionen

# %%
import_path = '../input/prep/bin/sturm1910_1911_0011.jpg'
filename = 'sturm1910_1911_0011.jpg'
export_path = '../output/1910_1911_0011/'

# %% [markdown]
# ```find_vertical_line``` 
# 
# Die Methode `find_vertical_line` zieht vertikale Linien durch ein übergebenes Bild, wenn dies möglich ist, das heißt wenn eine Linie mit mindestens der Länge `min_percentage * Höhe des Bildes` existiert, die gezogen werden kann. Eine Linie wird entlang weißer Pixel gezogen und beendet, sobald ein schwarzes Pixel auftaucht.
# 
# ### Input
# - *image*: binäres Bildobjekt, angelegt durch `imread` o.Ä.
# - *start_at*: Pixel, ab dem die Linie gezogen werden soll. In der ersten Iteration kann es sinnvoll sein hier z.B. 50 zu wählen. Dann hindert ein schmaler schwarzer Rand die Methode nicht daran, Linien zu ziehen
# - *min_percentage*: Minimale Länge einer Linie als Prozentteil der Seite
# 
# ### Output
# - *lines* : Liste aus Listen. Jede innere Liste repräsentiert eine Linie und hat das Format `[0, Spalte, Endzeile, Spalte]`
# 
# 
# 

# %%
def find_vertical_line(image, start_at, min_percentage):
    lines = []
    im_arr = numpy.asarray(image)
    print("v",im_arr.shape)
    num_rows, num_columns = im_arr.shape
    min_len = int(min_percentage*num_rows)
    for i in range(0, num_columns):
        row_position = start_at
        count = 0
        while (im_arr[row_position][i]):
            row_position += 1
            if(row_position == num_rows-1):
                break
            count += 1
        if(count > min_len):
            lines.append([0 , i , row_position, i])
    return lines

# %% [markdown]
# ```find_horizontal_line``` 
# 
# Die Methode `find_horizontal_line` zieht horizontale Linien durch ein übergebenes Bild, wenn dies möglich ist, das heißt wenn eine Linie mit mindestens der Länge `min_percentage * Breite des Bildes` existiert, die gezogen werden kann. Eine Linie wird entlang weißer Pixel gezogen und beendet, sobald ein schwarzes Pixel auftaucht.
# 
# ### Input
# - *image*: binäres Bildobjekt, angelegt durch `imread` o.Ä.
# - *start_at*: Pixel, ab dem die Linie gezogen werden soll. In der ersten Iteration kann es sinnvoll sein hier z.B. 50 zu wählen. Dann hindert ein schmaler schwarzer Rand die Methode nicht daran, Linien zu ziehen
# - *min_percentage*: Minimale Länge einer Linie als Prozentteil der Seite
# 
# ### Output
# - *lines* : Liste aus Listen. Jede innere Liste repräsentiert eine Linie und hat das Format `[Reihe, 0, Reihe, Endzeile]`
# 
# 
# 

# %%
def find_horizontal_line(image, start_at, min_percentage):
    lines = []
    im_arr = numpy.asarray(image)
    print("h", im_arr.shape)
    num_rows, num_columns = im_arr.shape
    #print(num_rows, num_columns)
    min_len = int(min_percentage*num_columns)
    for i in range(0, num_rows):
        col_position = start_at
        count = 0
        while(im_arr[i][col_position]):
            col_position += 1
            if(col_position == num_columns-1):
                break
            count += 1
        if(count > min_len):
            lines.append([i, 0, i, col_position])
    return lines

# %%
def find_vertical_line_clusters(lines):
    clusters = []
    if len(lines) == 0:
        return []
    first_line = lines[0]
    last_line = []
    for i in range (1, len(lines)):
        start_i = lines[i][1]
        start_prev = lines[i-1][1]
        if(abs(start_i - start_prev) > 5):
            last_line = lines[i-1]
            if last_line[1]-first_line[1] > 1:
                clusters.append((first_line, last_line))
            first_line = lines[i]
            last_line = []
    return clusters

# %%
def find_horizontal_line_clusters(lines):
    clusters = []
    if len(lines) == 0:
        return []
    first_line = lines[0]
    last_line = []
    for i in range (1, len(lines)):
        start_i = lines[i][0]
        start_prev = lines[i-1][0]
        if(abs(start_i-start_prev) > 5):
            last_line = lines[i-1]
            if last_line[0]-first_line[0] > 1:
                clusters.append((first_line, last_line))
            first_line = lines[i]
            last_line = []
    return clusters

# %%
def find_vertical_cuts(clusters):
    cuts = []
    for cluster in clusters:
        #print(cluster, cluster[1][1], cluster[0][1])
        cut = cluster[0][1] + int((cluster[1][1]-cluster[0][1])/2)
        cuts.append(cut)
    return cuts

# %%
def find_horizontal_cuts(clusters):
    cuts = []
    for cluster in clusters:
        cut = cluster[0][0] + int((cluster[1][0]-cluster[0][0])/2)
        cuts.append(cut)
    return cuts

# %%
def cut_page_vertically(image, cuts, debug):
    splitted_image = []
    offset = 0
    for i in range(0, len(cuts)):
        if(debug):
            print("Appending all coulmns til " + str(cuts[i]))
        splitted_image.append(image[:,:cuts[i]-offset])
        if(debug):
            print("Shape of splitted image: " + str(splitted_image[-1].shape))
        image = image[:,cuts[i]-offset:]
        offset += cuts[i]-offset
        if(debug):
            print("Shape of remaining image: "+str(image.shape))
    splitted_image.append(image)
    return splitted_image

# %%
def cut_page_horizontally(image, cuts, debug):
    splitted_image = []
    offset = 0
    for i in range(0, len(cuts)):
        if(debug):
            print("Appending all rows til "+str(cuts[i]))
        splitted_image.append(image[:cuts[i]-offset,:])
        if(debug):
            print("Shape of splitted image: "+str(splitted_image[-1].shape))
        image = image[cuts[i]-offset:,:]
        offset += cuts[i]-offset
        if(debug):
            print("Shape of remaining image: "+str(image.shape))
    splitted_image.append(image)
    return splitted_image

# %%
def slice_vertically(image, first_slice):
    if first_slice:
        lines = find_vertical_line(image, 50, 0.5)
    else:
        lines = find_vertical_line(image, 0, 0.95)
    clusters = find_vertical_line_clusters(lines)
    cuts = find_vertical_cuts(clusters)
    splitted_image = cut_page_vertically(image, cuts, False)
    return splitted_image
    

# %%
def slice_horizontally(image, first_slice):
    if first_slice:
        lines = find_horizontal_line(image, 50, 0.5)
    else:
        lines = find_horizontal_line(image, 0, 0.95)
    clusters = find_horizontal_line_clusters(lines)
    cuts = find_horizontal_cuts(clusters)
    splitted_image = cut_page_horizontally(image, cuts, False)
    return splitted_image

# %%
def generate_line_plot(image, lines):
    for l in lines:
        rr,cc = line(l[0], l[1], l[2], l[3])
        image[rr,cc] = 1
    return image


# %%
def test_lines(path):
    image = imread(path)
    v_lines = find_vertical_line(image, 50, 0.5)
    h_lines = find_horizontal_line(image, 50,0.5)
    #line_image = generate_line_plot(image, v_lines)
    line_image = generate_line_plot(image, h_lines)
    imsave('../output/lines.png', line_image)
    return v_lines, h_lines

# %%
def test_clusters(path, v_lines, h_lines):
    image = imread(path)
    #v_lines = find_vertical_line(image)
    #h_lines = find_horizontal_line(image)
    v_clusters = find_vertical_line_clusters(v_lines)
    print(len(v_clusters))
    h_clusters = find_horizontal_line_clusters(h_lines)
    print(len(h_clusters))
    lines = []
    for vc in v_clusters:
        print("Vertical cluster from" + str(vc[0][1]) + " to " + str(vc[1][1]))
        lines.append(vc[0])
        lines.append(vc[1])
    for hc in h_clusters:
        lines.append(hc[0])
        lines.append(hc[1])
    plot = generate_line_plot(image, lines)
    imsave('../output/clusters.png', plot)
    return v_clusters, h_clusters

# %%
def test_cuts(path, v_clusters, h_clusters):
    image = imread(path)
    v_cuts = find_vertical_cuts(v_clusters)
    h_cuts = find_horizontal_cuts(h_clusters)
    lines = []
    for cut in v_cuts:
        lines.append([0, cut, image.shape[0]-2, cut])
    for cut in h_cuts:
        lines.append([cut, 0, cut, image.shape[1]-2])
    plotimage = imread('../input/prep/gray/sturm1910_1911_0011.jpg')
    plot = generate_line_plot(plotimage, lines)
    imsave('../output/cuts.png', plot)
    return v_cuts, h_cuts

# %%
def test_pagecut(import_path, export_path, v_cuts, h_cuts):
    image = imread(import_path)
    print("Shape of original image: "+str(image.shape))
    print("Expected vertical cuts: ")
    for cut in v_cuts:
        print("at "+str(cut))
    print("Expected horizontal cuts: ")
    for cut in h_cuts:
        print("at "+str(cut))
    v_images = cut_page_vertically(image, v_cuts, True)
    h_images = cut_page_horizontally(image, h_cuts, True)
    k = 0
    for im in v_images:
        imsave(export_path+str(k)+'v.png', im)
        k += 1
    k = 0
    for im in h_images:
        imsave(export_path+str(k)+'h.png', im)
        k += 1


# %%
#def test(import_path, export_path):
 #   v_lines, h_lines = test_lines(import_path)
  #  v_clusters, h_clusters = test_clusters(import_path, v_lines, h_lines)
   # v_cuts, h_cuts = test_cuts(import_path, v_clusters, h_clusters)
    #test_pagecut(import_path, export_path, v_cuts, h_cuts)

# %%
def vertical_split(image, px_start, min_len, debug=False):
    lines = find_vertical_line(image, px_start, min_len)
    clusters = find_vertical_line_clusters(lines)
    #if(len(clusters)>10):
     #   print("Length of clusters: " + str(len(clusters)))
    cuts = find_vertical_cuts(clusters)
    return cut_page_vertically(image, cuts, debug)


# %%
def horizontal_split(image, px_start, min_len, debug=False):
    lines = find_horizontal_line(image, px_start, min_len)
    clusters = find_horizontal_line_clusters(lines)
    #if(len(clusters)>10):
     #   print("Length of clusters: " + str(len(clusters)))
    cuts = find_horizontal_cuts(clusters)
    return cut_page_horizontally(image, cuts, debug)

# %%
def number_of_cuts(image, px_start, min_len, direction, debug=False):
    if(direction=="h"):
        lines = find_horizontal_line(image, px_start, min_len)
        clusters = find_horizontal_line_clusters(lines)
        cuts = find_horizontal_cuts(clusters)
    elif(direction=="v"):
        lines = find_vertical_line(image, px_start, min_len)
        clusters = find_vertical_line_clusters(lines)
        cuts = find_vertical_cuts(clusters)
    return(len(cuts))

# %%
def flip_direction(direction):
    if direction == "v":
        return "h"
    else:
        return "v"

# %%
def more_splits(image, px_start, min_len, direction):
    if(number_of_cuts(image, px_start, min_len, direction) > 1):
        return True
    else:
        return False

# %%
def save_images(images, path, it, k):
    add = False
    for im in images:
        r, c = im.shape
        if r < 100 or c < 100:
            continue
        imsave(path + "/" + str(it) + "_" + str(k) + ".png", im)
        #print("Saving " + path + "/" + str(it) + "_" + str(k) + ".png")
        k += 1
        add = True
    return add, k+1
    

# %%
def too_small(image):
    r, c = image.shape
    if r < 150 or c < 150:
        return True
    else:
        return False
    

# %%
def square_pix(image):
    r, c = image.shape
    return r*c

# %% [markdown]
# ### Routine

# %%
in_path = "../input/prep/bin/sturm1910_1911_0091.png"
#in_path = "../output/test/1h.png"
out_path = "../output/test/"
#test(in_path, out_path)

# %%
path = '../input/prep/bin'
out_path = '../output'
min_len = 0.8


def __main__():
    for filename in os.listdir(path):
        #if filename != "sturm1910_1911_0091.png":
            #continue
        file_out_path = out_path + "/" + filename[:-4]
        try:
            os.mkdir(file_out_path)
        except: 
            for imname in os.listdir(file_out_path):
                os.remove(file_out_path+"/"+imname)
        shutil.copyfile(path + "/" + filename, file_out_path + "/" + filename)
        print("===== Processing File " + filename + " =====")
        

        flag = True
        first = True
        direction = "h"
        it = 0
        k = 0

        while(flag):
            flag = False
            for filename in os.listdir(file_out_path):
                image = imread(file_out_path + "/" + filename)
                #print("Iteration : " + str(it))

                if first:
                    ims = horizontal_split(image, 20, 0.5)
                    add, k = save_images(ims, file_out_path, it, k)
                    first = False
                    #direction = "v"
                    os.remove(file_out_path + "/" + filename)
                    flag = True
                    break


                elif direction == "h":
                    #print("filename: " + filename + " " + direction + " it " + str(it) + " More splits: " + str(more_splits(image, 0,min_len, "h")) + " too small: " + str(too_small(image)))
                    if(more_splits(image, 0, min_len, "h") and not too_small(image)):
                        flag = True
                        ims = horizontal_split(image, 0, min_len)
                        add, k = save_images(ims, file_out_path, it, k)
                        #direction = "v"
                        if add:
                            os.remove(file_out_path + "/" + filename)
                            #print("Deleting " + filename)
                        continue
                    #direction = "v"

                elif direction == "v":
                    #print("filename: " + filename + " " + direction + " it "  + str(it) + " More splits: " + str(more_splits(image, 0,min_len, "v")) + " too small: " + str(too_small(image)))
                    if(more_splits(image, 0, min_len, "v") and not too_small(image)):
                        flag = True
                        ims = vertical_split(image, 0, min_len)
                        add, k = save_images(ims, file_out_path, it, k)
                        #direction = "h"
                        if add:
                            os.remove(file_out_path + "/" + filename)
                            #print("Deleting " + filename)
                        continue
                    #direction = "h"

            it += 1
            direction=flip_direction(direction)
            k = 0
            
            if it == 5:
                flag = False


            



# %%



