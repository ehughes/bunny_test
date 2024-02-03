import cv2
import numpy as np
import imageio
skip = 0;
quit = False

FAST_FORWARD_TO_DEMO = False
WRITE_PNGS = False

PREDATOR_START_FRAME = 240

RECT_PHASE1_START_FRAME = 330
RECT_PHASE2_START_FRAME = 740
RECT_PHASE3_START_FRAME = 800
OFF_FRAME = 930

FRAME_RANGE_START = 750
FRAME_RANGE_END = 1000

GIF_NAME = "target_engaged.gif"

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

def LCD_color2(b,g,r):

  packed = int(0)

  r = r>>6
  g = g>>6
  b = b>>6
  

  packed |= r<<4
  packed |= g<<2
  packed |= b<<0
  


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
            f.write(str(LCD_color2((p[0]),(p[1]),(p[2]))) + ',');
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
 

Scale = int(2)

width = 320 * Scale;
height = int(width * 480.0/640.0);

rectf = (150*Scale, 80*Scale)
dimf = (40*Scale,40*Scale)
rectf_step = (.05*Scale, .002*Scale)
dimf_step = (.00025*Scale, .00025*Scale)


fourcc = cv2.VideoWriter_fourcc(*'MJPG')
vout = cv2.VideoWriter('output3.avi',fourcc , 30.0, (width,height*2))

gif_writer = imageio.get_writer(GIF_NAME, mode='I', fps=30)


skip = 0;
frame_num = 0
FrameCount = 0;

CaptureStartFrame = 750

skip_step = 4

TotalFrames = 20

box_scale = 0
BOX_SCALE_FRAMES = 30

WriteFrames = True;

FrameDelay = 10
# OpenCV2 quantize color
# Read until video is completed
while(cap.isOpened() and quit == False):
  # Capture frame-by-frame
  ret, frame = cap.read()
  if ret == True:
    
    frame_num = frame_num + 1

    if(FAST_FORWARD_TO_DEMO == True):
      if(frame_num < PREDATOR_START_FRAME):
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


    if(frame_num > PREDATOR_START_FRAME and frame_num < RECT_PHASE1_START_FRAME):
      #red edges
      edge2[:,:,1] = np.zeros([edge2.shape[0], edge2.shape[1]]) 
      edge2[:,:,0] = np.zeros([edge2.shape[0], edge2.shape[1]])
    elif(frame_num >= RECT_PHASE1_START_FRAME and frame_num < OFF_FRAME):
      edge2[:,:,1] = np.zeros([edge2.shape[0], edge2.shape[1]]) 
      edge2[:,:,2] = edge2[:,:,2] 
      edge2[:,:,0] = np.zeros([edge2.shape[0], edge2.shape[1]])
    elif(frame_num <= PREDATOR_START_FRAME):
      edge2[:,:,2] = np.zeros([edge2.shape[0], edge2.shape[1]])
      edge2[:,:,1] = edge2[:,:,1] 
      edge2[:,:,0] = np.zeros([edge2.shape[0], edge2.shape[1]])
    else:
      edge2[:,:,2] = np.zeros([edge2.shape[0], edge2.shape[1]])
      edge2[:,:,1] = edge2[:,:,1]
      edge2[:,:,0] = np.zeros([edge2.shape[0], edge2.shape[1]])
      pass



    #blue edges
    #edge2[:,:,2] = np.zeros([edge2.shape[0], edge2.shape[1]])
    #edge2[:,:,1] = np.zeros([edge2.shape[0], edge2.shape[1]])

    #cyan edges
    #edge2[:,:,2] = np.zeros([edge2.shape[0], edge2.shape[1]])
    
   
    #yellow edges
    #edge2[:,:,0] = np.zeros([edge2.shape[0], edge2.shape[1]])

    #white edges
    

    #dst = cv2.add(frame,edge2)
            
    dst = cv2.addWeighted(gray_image2, alpha, edge2, beta, 0.0)

    if(frame_num >= RECT_PHASE1_START_FRAME and frame_num < OFF_FRAME):

      mask = cv2.resize(np.zeros((width,height,3), dtype=np.uint8),(width,height))

      if(frame_num == RECT_PHASE1_START_FRAME):
         rectf = (150*Scale, 80*Scale)
         dimf = (40*Scale,40*Scale)
         rectf_step = (.016*Scale, .0004*Scale)
         dimf_step = (.009*Scale, .009*Scale)
      elif(frame_num == RECT_PHASE2_START_FRAME):
         rectf_step = (.2*Scale, -.1*Scale)
         dimf_step = (.4*Scale, .25*Scale)
      elif(frame_num == RECT_PHASE3_START_FRAME):
         rectf_step = (.2*Scale, -.25*Scale)
         dimf_step = (1.45*Scale, .65*Scale)

      rectf = (rectf[0] + rectf_step[0] , rectf[1] + rectf_step[1])
      dimf = (dimf[0] + dimf_step[0] , dimf[1] + dimf_step[1])

      if(box_scale <= BOX_SCALE_FRAMES):
   
          box_width = (rectf[0] + dimf[0] - rectf[0])
          box_height = (rectf[1] + dimf[1] - rectf[1])
          center_x = rectf[0] + box_width / 2
          center_y = rectf[1] + box_height / 2

          #scaled_width = box_width * (8 *(1 - box_scale/BOX_SCALE_FRAMES) + 1)
          #scaled_height = box_height * (8 *(1 - box_scale/BOX_SCALE_FRAMES) + 1)

          scaled_width = box_width *  box_scale/BOX_SCALE_FRAMES
          scaled_height = box_height * box_scale/BOX_SCALE_FRAMES
          

          box_scale = box_scale + 1
        
          x1 = center_x - scaled_width / 2
          y1 = center_y - scaled_height / 2
          x2 = center_x + scaled_width / 2
          y2 = center_y + scaled_height / 2
      else:
          x1 = rectf[0]
          y1 = rectf[1]
          x2 = rectf[0] + dimf[0]
          y2 = rectf[1] + dimf[1]


      mask = cv2.rectangle(mask, (int(x1),int(y1)), (int(x2) , int(y2)), (255, 255, 255), -1)
    
      no_ai= frame.copy()
    
    
      mask_inv = 255 - mask

      outf = cv2.bitwise_and(mask,img_blur2)
      
      dst = cv2.bitwise_and(mask_inv,dst)
    
      dst = cv2.bitwise_or(outf,dst)

      dst = cv2.rectangle(dst, (int(x1),int(y1)), (int(x2) , int(y2)), (0, 0, 255), 2)



    ##box_only = cv2.rectangle(frame, (int(rectf[0]),int(rectf[1])), (int(rectf[0] + dimf[0]) , int(rectf[1] + dimf[1])), (0,0, 255), 2)
    




    div = 64

    f2 = dst // div * div 
   
    #f2 = cv2.GaussianBlur(f2, (3,3), 0)
   
    f2 = f2 // div * div 



    #outf = dst
    cat = np.concatenate((no_ai, f2), axis=0)
  
  



    cv2.imshow('Frame',cat)
    cv2.setMouseCallback("Frame", click_and_crop)
 

          
    dst=cv2.transpose(dst)
    ##no_ai=cv2.transpose(no_ai)
    ##box_only=cv2.transpose(box_only)



    print("Frame " + str(frame_num))

    if(skip == 0):
      if(frame_num >CaptureStartFrame and FrameCount < TotalFrames):

        cv2.imwrite('./frames/frame_' + str(FrameCount) + '.png', dst)
  
        if(WRITE_PNGS == True):
          if(WriteFrames):
            if(FrameCount == 0):
                
                start_c_png('frame', 'frame','frame', dst)
                ##start_c_png('frame', 'frame_no_ai','frame',no_ai)
                ##start_c_png('frame','frame_box_only','frame', box_only)
    
                print("Starting Frame write")

            FrameCount = FrameCount + 1; 
            write_c_png('frame','frame','frame', dst)
            #write_c_png('frame','frame_no_ai','frame', no_ai)
            #write_c_png('frame','frame_box_only','frame', box_only)
            
                  
            print("writing Frame # " + str(FrameCount))
            
            if(FrameCount >= TotalFrames):
              stop_c_png('frame','frame','frame', dst)
              ##stop_c_png('frame','frame_no_ai','frame', no_ai)
              ##stop_c_png('frame','frame_box_only','frame', box_only)
            
              print("stopping Frame write")
              FrameCount = 100000
              break
         
    skip = skip + 1
    if(skip>skip_step):
       skip = 0

    if(frame_num >= FRAME_RANGE_START and frame_num <= FRAME_RANGE_END):
      vout.write(cat)
      #gif_writer.append_data(cv2.cvtColor(f2, cv2.COLOR_BGR2RGB))
      gif_writer.append_data(cv2.cvtColor(f2, cv2.COLOR_BGR2RGB))
      

    # Press Q on keyboard to  exit
    if (cv2.waitKey(FrameDelay) & 0xFF == ord('q')): 
      break
 
    
    #print('frame' + str(frame_num));
  
  # Break the loop
  else: 
    break

gif_writer.close()
vout.release()
# When everything done, release the video capture object
cap.release()

# Closes all the frames
cv2.destroyAllWindows()