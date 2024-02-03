import cv2
import numpy as np

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

top = cv2.imread('warn.png');
bottom = cv2.imread('az.png');

start_c_png('top','top','top', top)
write_c_png('top','top','top', top)
stop_c_png('top', 'top','top',top)

start_c_png('bottom','bottom','bottom', bottom)
write_c_png('bottom','bottom','bottom', bottom)
stop_c_png('bottom','bottom','bottom', bottom)

