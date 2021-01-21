import numpy as np
import cv2
from tkinter import filedialog
from tkinter import *
import ctypes  
import sys 
import time



# error message
def Mbox(title, text, style):
    return ctypes.windll.user32.MessageBoxW(0, text, title, style)


# to resize background image as camera image
def resize(img_under_operation,img):
	width = img.shape[1]
	height = img.shape[0]
	dim = (width, height)
	resized = cv2.resize(img_under_operation, dim, interpolation = cv2.INTER_AREA)
	return resized

# Open vedio from browser

vcap = cv2.VideoCapture(1)
#vcap = cv2.VideoCapture(0)
vcap.set(cv2.CAP_PROP_FPS, 30)


# To check whether camera is working or not
if not vcap.isOpened():
    
    mess_title = "Internet issue"
    mess_content= 'cannot reach connected mobile/device/integreted camera( Sasta internet )'
    Mbox(mess_title,mess_content, 0)
    sys.exit()
    
# capture first frame(original_background)
res1, frame1 = vcap.read()

# load virtual background image
a= None
root = Tk()
root.filename =  filedialog.askopenfilename(initialdir = "/",title = "Select file")
a = root.filename

# if file is empty or not of suitable type, then generate error 
if ('.jpg' or '.png' or '.jpeg') not in a:
    Mbox("Image import errror","No image is selected", 0)
    sys.exit()

# storing virtual background in active object
virtual_background = cv2.VideoCapture(a)
res2, bg = virtual_background.read()
bg = resize(bg,frame1)
reset_from_blur = bg
root.destroy()
# Pointer to dffrentiate between display and recording of background
background_captured = 0

while(True):
    # Capture frame-by-frame in loop
    res1, frame_rest = vcap.read()

    if background_captured == 0:
        frame1 = frame_rest

    # subtracting images to get body parts
    first_cutout= cv2.subtract(frame1,frame_rest)
    second_cutout=cv2.subtract(frame_rest,frame1)

    final_diff = first_cutout+second_cutout  
    final_diff[abs(final_diff)<17.0] = 0   
   
    convert_to_gray = cv2.cvtColor(final_diff.astype(np.uint8), cv2.COLOR_BGR2GRAY)
    convert_to_gray[np.abs(convert_to_gray) < 11.0] = 0

    body_in_white = convert_to_gray.astype(np.uint8)
   #   # <- testing case(to make body in focus)
    body_in_white[body_in_white>0]=255
    
    body_in_black = cv2.bitwise_not(body_in_white)
    
    # Extracted body and background parts
    extracted_body_in_color = cv2.bitwise_and(frame_rest,frame_rest,mask = body_in_white)
    extracted_background_in_color = cv2.bitwise_and(bg,bg,mask = body_in_black)
    
    # Final image
    finalised_virtual_image = cv2.add(extracted_background_in_color,extracted_body_in_color)
    

    if finalised_virtual_image is not None:
        # Display the resulting frame
        cv2.imshow('frame',finalised_virtual_image )
        

        key = cv2.waitKey(30) & 0xFF
        # Press q to close the video windows before it ends if you want
        if key == ord('q'):
            print("Command: Quit")
            break
        elif key == ord('d'):
            background_captured = 1
            print('Command: Background captured for virtual Background')
        elif key == ord('b'):
            # Blur Effect on background
            bg = cv2.GaussianBlur(bg,(3,3),0)
            print("Command:Background is blur") 
        elif ord('r') == key:
            background_captured = 0
            background_blur = 0
            bg = reset_from_blur
            print("Command: System is Reset")
    
    else:
        print("System:Not able to receive Frames from browser, Please check your connection ")
        Mbox('Internet issue',"please check your internet connection",0)
        break

# When everything done, release the capture
vcap.release()
cv2.destroyAllWindows()
print("System stop")