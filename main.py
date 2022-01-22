from PIL import Image, ImageTk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from logging import getLogger, basicConfig, DEBUG
from tkinter import ttk
import random
from tkinter import messagebox, Button, Label, StringVar, Entry, NW, Tk, OptionMenu, Canvas, TOP, BOTH, IntVar, Checkbutton
basicConfig(filename='./myapp.log', level=DEBUG, 
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger=getLogger(__name__)
try:
    m = [0,48,12,60, 3,51,15,63,
        32,16,44,28,35,19,47,31,
        8,56, 4,52,11,59, 7,55,
        40,24,36,20,43,27,39,23,
        2,50,14,62, 1,49,13,61,
        34,18,46,30,33,17,45,29,
        10,58, 6,54, 9,57, 5,53,
        42,26,38,22,41,25,37,21]
    M = [list(map(lambda x: x / 64, m[i:i+8])) for i in range(0, len(m), 8)]

    def pixelate(img):
        return img

    def reverse(x):
        result = 0
        n = len(bin(x))-2
        for i in range(n):
            if (x >> i) & 1: result |= 1 << (n - 1 - i)
        return result

    def ordered_dither(img, mask):
        M      = mask
        n      = len(mask)
        pixels = img.load()
        wt = int(wthreshold.get())
        bt = int(bthreshold.get())
        for i in range(img.size[0]):
            for j in range(img.size[1]):
                pixels[i, j] = 255 if pixels[i, j]/255 > M[i%n][j%n] and pixels[i, j] > wt or (not pixels[i, j] < bt) else 0
        return img

    def random_dither(img):
        wt = int(wthreshold.get())
        bt = int(bthreshold.get())
        pixelss = img.load()
        for i in range(img.size[0]):
            for j in range(img.size[1]):
                if pixelss[i, j] >= bt:
                    pixelss[i, j] = 255
                elif pixelss[i, j] <= wt:
                    pixelss[i, j] = 0
                else:
                    pixelss[i, j] = 255 if pixelss[i, j] > random.randrange(0,255) else 0
        return img
                
    def fs_dither(img):
        pixelss = img.load()
        pixels  = [[0]*img.size[1] for i in range(img.size[0])]
        wt = int(wthreshold.get())
        bt = int(bthreshold.get())
        for i in range(img.size[0]):
            for j in range(img.size[1]):
                if pixelss[i, j] >= bt:
                    pixelss[i, j] = 255
                if pixelss[i, j] <= wt:
                    pixelss[i, j] = 0
        for i in range(img.size[0]):
            for j in range(img.size[1]):
                pix = pixelss[i, j]/255+pixels[i][j]
                new_pix = round(pix) >= 0.5
                pixelss[i, j] =  new_pix*255
                qerror = pix-new_pix
                if True:
                    try:
                        pixels[i + 1][j] += qerror * 5 /  16
                    except:
                        pass
                    try:
                        pixels[i + 1][j + 1] += qerror * 1 / 16
                    except:
                        pass
                    try:
                        pixels[i][j + 1] += qerror * 7 / 16
                    except:
                        pass
                    try:
                        if j != img.size[1]:
                            pixels[i + 1][j - 1] += qerror * 3 / 16
                    except:
                        pass
        return img

    def resize(img, q, mode):
        return img.resize((int(img.size[0]*q), int(img.size[1]*q)), resample=mode)

    def crop(img):
        img1 = img.resize((400-30, int(img.size[1]*(400-30)/img.size[0])))
        if img1.size[1] > 270-30:
            img1 = img1.crop((0,(img1.size[1]-(270-30))//2,400-30,(img1.size[1]-(270-30))//2+270-30))
        return img1

    def select_img():
        global img, tkimg1, imgonscreen, canvas
        filename = askopenfilename(defaultextension=".png", filetypes=[("Images",".png .jpg .bmp")])
        img = Image.open(filename)
        tkimg1 = ImageTk.PhotoImage(image = crop(img))
        canvas.create_image((30,30), image = tkimg1, anchor= NW)

    def process():
        global img, tkimg2, canvas, convimg
        try:
            img
        except:
            img = None
            messagebox.showerror("Error", "No image selected")
            return
        q = float(sfactor.get())
        if not 0 < q <= 1:
            messagebox.showerror("Error", "Wrong resize factor")
            return
        size = img.size
        option = another.get()
        if option != "Pixelate":
            rimg = resize(img, q, Image.ANTIALIAS)
        else:
            rimg = resize(img, q, Image.NEAREST)
        if option == "Random":  
            #rimg = fs_dither(rimg)
            rimg = random_dither(rimg.convert('L'))
        elif option == "Ordered":
            rimg = ordered_dither(rimg.convert('L'), M)
        elif option == "FS":
            rimg = fs_dither(rimg.convert('L'))
        elif option == "Pixelate":
            rimg = pixelate(rimg)
        else:
            messagebox.showerror("Error", "Select the dithering metod")
            return
        rimg = rimg.resize((rimg.size[0]*(size[0]//rimg.size[0]), rimg.size[1]*(size[1]//rimg.size[1])), Image.NEAREST)
        convimg = rimg
        tkimg2 = ImageTk.PhotoImage(image = crop(rimg))
        print(another.get())
        canvas.create_image((30,300), image = tkimg2, anchor= NW)
    
    def show_image():
        global convimg, img
        try:
            convimg
        except:
            try:
                convimg = img
            except:
                messagebox.showerror("Error", "No message to display")
        simg = convimg
        simg.show()
    
    def save_image():
        global convimg
        try:
            convimg
        except:
            messagebox.showerror("Error", "No image to save")
            return
        path = asksaveasfilename(defaultextension = ".png", filetypes=[("Images",".png .jpg .bmp")], initialfile = "dithered.png")
        convimg.save(path)
        messagebox.showinfo("Succeed", "Image saved to %s" % path)
    
    window = Tk()
    canvas = Canvas(window, width = 560, height = 300+270-1)
    window.resizable(width=False, height=False)
    
    item1 = canvas.create_rectangle(30, 30, 400-1, 270-1,
                outline="grey82", fill="grey82")
    item1 = canvas.create_rectangle(30, 300, 400-1, 300+270-1-30,
                outline="grey82", fill="grey82")
    
    select = Button(text = "Select image", command = select_img)
    select.place(x = 410, y = 30, width = 100, height = 35)
    
    label = Label(text="Scale factor 0.0-1.0:")
    label.place(x = 410, y = 30+35+20)
    sfactor = StringVar()
    
    sfactor_ = Entry(textvariable=sfactor, font=("Courier", 16))
    sfactor_.place(x = 410, y = 30+35+20+25, width = 100)
    sfactor.set("1")
    
    wlabel1 = Label(text="Black threshold 0-255:")
    wlabel1.place(x = 410, y = 30+35+20+25+35+25)
    wthreshold = StringVar()
    wthreshold.set("10")
    wtreshold_ = Entry(textvariable = wthreshold, font = ("Courier", 16))
    wtreshold_.place(x = 410, y = 30+35+20+25+35+25+25, width = 100)
    
    credit = Label(text="by r_4spberry 2022")
    credit.place(x = 430, y = 580-50-8)
    
    blabel1 = Label(text="White threshold 0-255:")
    blabel1.place(x = 410, y = 30+35+20+25+35+25+50)
    bthreshold = StringVar()
    bthreshold.set("245")
    btreshold_ = Entry(textvariable = bthreshold, font = ("Courier", 16))
    btreshold_.place(x = 410, y = 30+35+20+25+35+25+25+50, width = 100)
    
    another = StringVar()
    mode = OptionMenu(window, another, "Ordered", "FS", "Random", "Pixelate")
    mode.place(x = 407, y = 30+35+20+25+33, width = 130)
    another.set("Select Algorithm")
    
    run = Button(text = "Run", command = process)
    run.place(x = 410, y = 300, width = 100, height = 35)
    
    show = Button(text = "Show image", command = show_image)
    show.place(x = 410, y = 300+35+20, width = 100, height = 35)
    
    save = Button(text = "Save", command = save_image)
    save.place(x = 410, y = 300+35+20+35+20, width = 100, height = 35)
    
    canvas.pack(side = TOP, expand=True, fill=BOTH)
    
    window.mainloop()
except Exception as err:
    logger.error(err)
    print(err)