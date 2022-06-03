from PIL import Image

class Box:
    top_left = 0
    top_right = 0
    bottom_left = 0
    bottom_right = 0
    depth = 0
    height = 0
    width = 0
    size = (0,0)
    contains_ad = True

    def __init__(self, tl, tr, bl, br, depth):
        if(br <= tr or bl <= tl):
            raise ValueError("bl and br are too small")
        self.top_left = tl
        self.top_right = tr
        self.bottom_left = bl
        self.bottom_right = br
        self.depth = depth
        self.height = abs(self.bottom_left[1]-self.top_left[1])
        self.width = abs(self.top_right[0] - self.top_left[0])
        self.size = (self.width, self.height)

    def split(self, at, orientation):
        # horizontal
        if orientation:
            if(at-self.top_left[1] < 50):
                return None
            new_box = Box(self.top_left, self.top_right, (self.top_left[0], at), (self.top_right[0], at), self.depth+1)
            self.top_left = (self.bottom_left[0], at)
            self.top_right = (self.bottom_right[0], at)
            self.update()
            print(" ====== splitting horizontal =====")
            print("new box")
            new_box.to_print()
            print("self")
            self.to_print()
            return(new_box)
        #vertical
        else:
            if(at-self.top_left[0] < 200):
                return None
            new_box = Box(self.top_left, (at, self.top_left[1]), self.bottom_left, (at, self.bottom_left[1]), self.depth+1)
            self.top_left = (at, self.top_right[1])
            self.bottom_left = (at, self.bottom_right[1])
            self.update()
            print("===== splitting vertical =====")
            print("new box")
            new_box.to_print()
            print("self")
            self.to_print()
            return(new_box)

    
    def update(self):
        self.height = abs(self.bottom_left[1]-self.top_left[1])
        self.width = abs(self.top_right[0] - self.top_left[0])
        self.size = (self.width, self.height)

    def fit_image(self, image):
        image = image.crop([self.top_left[0], self.top_left[1], self.bottom_right[0], self.bottom_right[1]])
        print("Size of fitted image: ", image.width, image.height)
        return(image)

    def to_print(self):
        print("tl: ", self.top_left, "\ntr: ", self.top_right, "\nbl: ", self.bottom_left, "\nbr: ", self.bottom_right, "\nsize: ", self.size, "\ndepth: ", self.depth)


    def is_in_box(self, x, y):
        if(x > self.top_left[0] and x < self.top_right[0] and y > self.top_left[1] and y < self.bottom_left[1]):
            return True
        else: return False

    def merge(self, box):
        self.top_left = (min(self.top_left[0], box.top_left[0]), min(self.top_left[1], box.top_left[1]))
        self.top_right = (max(self.top_right[0], box.top_right[0]), self.top_left[1])
        self.bottom_left = (self.top_left[0], max(self.bottom_left[1], box.bottom_left[1]))
        self.bottom_right = (self.top_right[0], self.bottom_left[1])
        self.depth -= 1
    
    def to_dict(self):
        dict = {
        "top_left":self.top_left,
        "top_right":self.top_right,
        "bottom_left":self.bottom_left,
        "bottom_right":self.bottom_right,
        "depth":self.depth,
        "height":self.height,
        "width":self.width,
        "size":self.size,
        "contains_ad":self.contains_ad
        }
        return dict
