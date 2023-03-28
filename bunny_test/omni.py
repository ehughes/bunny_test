import cv2
import numpy as np
 
skip = 0;
quit = False

#Output pixel format: xxRGBrgb
FrameCount = 0;

def LCD_color(b,g,r):

  packed = int(0)

  r = r>>6
  g = g>>6
  b = b>>6
  

  packed |= ((r & (1 << 1))>>1) << 5; # R
  packed |=  (r & (1 << 0))<<2;    # r

  packed |= ((g & (1 << 1))>>1) << 4; # G
  packed |= (g & (1 << 0)) << 1;    # g

  packed |= ((b & (1 << 1))>>1) << 3; # B
  packed |= (b & (1 << 0)) << 0;    # b

  return packed

var_string = ''
  
def start_c_png(name,c_file_name,h_file_name, data):
    
    global var_string

    filename = c_file_name + '.c'
    headername = h_file_name + '.h'
    height, width = data.shape[:2]

    print('Start capture')
    with open(filename, 'w') as f:
        
        f.write('#include <stdint.h>\n');
        f.write('#include \"' + str(headername) + '\"\r\n');

        var_string = 'const uint8_t ' + name + '[]'

        f.write(var_string + ' = {\n')

        f.write('\n')        


def stop_c_png(name,c_file_name,h_file_name, data):
    filename = c_file_name + '.c'
    headername = h_file_name + '.h'
    height, width = data.shape[:2]

    print('Stop capture')

    with open(filename, 'a') as f:
        
        f.write('\n};')
        print('here')

    with open(headername, 'w') as f:
        
      f.write('#include <stdint.h>\n');

      f.write('\n');
    
      f.write('#ifndef __' + name.upper() + '_H\n');
      f.write('#define __' + name.upper() + '_H\n\r');


      f.write('#define ' + name.upper() + '_FRAME_COUNT ' + str(FrameCount) + '\n');
      f.write('#define ' + name.upper() + '_WIDTH ' + str(width) + '\n');
      f.write('#define ' + name.upper() + '_HEIGHT '+ str(height) + '\n\n');
      f.write('extern ' + var_string + ';\n');
      
      f.write('\n');

      f.write('#endif\n');

def write_c_png(name,c_file_name,h_file_name, data):
    
    global FrameCount
    filename = c_file_name + '.c'
    headername = h_file_name + '.h'
    height, width = data.shape[:2]

    with open(filename, 'a') as f:
        
        for y in range(height):
          for x in range(width):
            p = data[y][x]
            f.write(str(LCD_color((p[0]),(p[1]),(p[2]))) + ',');
          f.write('\n')
       


def click_and_crop(event, x, y, flags, param):
	# grab references to the global variables
	global quit
	# if the left mouse button was clicked, record the starting
	# (x, y) coordinates and indicate that cropping is being
	# performed
	if event == cv2.EVENT_LBUTTONDOWN:
		  quit = True; 



top = cv2.imread('warn.png');
bottom = cv2.imread('az.png');

start_c_png('top','top','top', top)
write_c_png('top','top','top', top)
stop_c_png('top', 'top','top',top)

start_c_png('bottom','bottom','bottom', bottom)
write_c_png('bottom','bottom','bottom', bottom)
stop_c_png('bottom','bottom','bottom', bottom)


# how apply edge detection in opencv python 

# Create a VideoCapture object and read from input file
# If the input is the camera, pass 0 instead of the video file name
cap = cv2.VideoCapture('bunny-concept-640-480.mp4')
#cap = cv2.VideoCapture('c:/ELI/pico_examples/pico-examples/blink/videoplayback.mp4')
 
# Check if camera opened successfully
if (cap.isOpened()== False): 
  print("Error openingS video stream or file")
 
width = 272;
height = int(width * 480.0/640.0);

fourcc = cv2.VideoWriter_fourcc(*'MP4V')
vout = cv2.VideoWriter('output3.mp4',0x7634706d , 30.0, (width*2,height))

skip = 0;
frame_num = 0
FrameCount = 0;

CaptureStartFrame = 750

skip_step = 4

TotalFrames = 36

rectf = (130, 63)
dimf = (45,42)

rectf_step = (.32, -.1)
dimf_step = (.62, .32)

WriteFrames = True

FrameDelay = 20
# OpenCV2 quantize color
# Read until video is completed
while(cap.isOpened() and quit == False):
  # Capture frame-by-frame
  ret, frame = cap.read()
  if ret == True:
    
    frame_num = frame_num + 1

    if(frame_num < CaptureStartFrame):
       continue

    frame = cv2.resize(frame,(width,height))
   # frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    div = int(64) 
    

    no_ai = frame

    f2 = frame 
   

   
    gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    img_blur = cv2.GaussianBlur(gray_image, (9,9), 0)

    img_blur2 = cv2.GaussianBlur(frame, (1,1), 0)

    edge = cv2.Canny(img_blur, 40, 60 )

    alpha = 0.55
    beta = (1.0 - alpha)


    edge2 = cv2.cvtColor(edge, cv2.COLOR_GRAY2BGR)
    gray_image2 = cv2.cvtColor(gray_image, cv2.COLOR_GRAY2BGR)
    edge2[:,:,2] = np.zeros([edge2.shape[0], edge2.shape[1]])
    edge2[:,:,0] = np.zeros([edge2.shape[0], edge2.shape[1]])

  
   
    #dst = cv2.add(frame,edge2)
    dst = cv2.addWeighted(gray_image2, alpha, edge2, beta, 0.0)

    mask = cv2.resize(np.zeros((width,height,3), dtype=np.uint8),(width,height))

    mask = cv2.rectangle(mask, (int(rectf[0]),int(rectf[1])), (int(rectf[0] + dimf[0]) , int(rectf[1] + dimf[1])), (255, 255, 255), -1)

    no_ai= frame.copy()

    box_only = cv2.rectangle(frame, (int(rectf[0]),int(rectf[1])), (int(rectf[0] + dimf[0]) , int(rectf[1] + dimf[1])), (0,0, 255), 2)

   

    mask_inv = 255 - mask

    outf = cv2.bitwise_and(mask,img_blur2)

    
    dst = cv2.bitwise_and(mask_inv,dst)
   
    dst = cv2.bitwise_or(outf,dst)

    dst = cv2.rectangle(dst, (int(rectf[0]),int(rectf[1])), (int(rectf[0] + dimf[0]) , int(rectf[1] + dimf[1])), (0, 0, 255), 2)



    #outf = dst
    cat = np.concatenate((no_ai, dst,box_only), axis=1)
  
    rectf = (rectf[0] + rectf_step[0] , rectf[1] + rectf_step[1])
    dimf = (dimf[0] + dimf_step[0] , dimf[1] + dimf_step[1])



    cv2.imshow('Frame',cat)
    cv2.setMouseCallback("Frame", click_and_crop)
 

    print("Frame " + str(frame_num))

    if(skip == 0):
      if(frame_num >CaptureStartFrame and FrameCount < TotalFrames):

        cv2.imwrite('c:/ELI/pico_examples/pico-examples/blink/frames/frame_' + str(FrameCount) + '.png', outf)
  
   
        if(WriteFrames):
          if(FrameCount == 0):
              
              start_c_png('frame', 'frame','frame', dst)
              start_c_png('frame', 'frame_no_ai','frame',no_ai)
              start_c_png('frame','frame_box_only','frame', box_only)
   
              print("Starting Frame write")

          FrameCount = FrameCount + 1; 
          write_c_png('frame','frame','frame', dst)
          write_c_png('frame','frame_no_ai','frame', no_ai)
          write_c_png('frame','frame_box_only','frame', box_only)
           
                 
          print("writing Frame # " + str(FrameCount))
          
          if(FrameCount >= TotalFrames):
            stop_c_png('frame','frame','frame', dst)
            stop_c_png('frame','frame_no_ai','frame', no_ai)
            stop_c_png('frame','frame_box_only','frame', box_only)
           
            print("stopping Frame write")
            FrameCount = 100000
            break
         
    skip = skip + 1
    if(skip>skip_step):
       skip = 0

    #vout.write(cat)
    # Press Q on keyboard to  exit
    if (cv2.waitKey(FrameDelay) & 0xFF == ord('q')): 
      break
 
    
    #print('frame' + str(frame_num));
  
  # Break the loop
  else: 
    break

vout.release()
# When everything done, release the video capture object
cap.release()

# Closes all the frames
cv2.destroyAllWindows()