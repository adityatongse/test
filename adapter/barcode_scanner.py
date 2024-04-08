import cv2
import numpy as np
from pyzbar.pyzbar import decode
import winsound

def scan():
    def decoder(image):
        gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        barcode = decode(gray_img)
    
        # Initialize barcodeData outside the loop
        barcodeData = None
    
        for obj in barcode:
            rect = obj.rect
            points = obj.polygon
            pts = np.array(points, np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(image, [pts], True, (0, 255, 0), 3)
    
            barcodeData = obj.data.decode("utf-8")
            barcodeType = obj.type
            string = "Data " + str(barcodeData) + " | Type " + str(barcodeType)
            cv2.putText(image, string, (rect[0], rect[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
    
        # Print barcode data even if no barcode is detected 
        return barcodeData
    
    cap = cv2.VideoCapture(0)
    result=""
    keep_window_open=True
    while keep_window_open:
        ret, frame = cap.read()
        result = decoder(frame)
        cv2.imshow('Image', frame)
        try :
            cv2.setWindowProperty('Image',cv2.WND_PROP_TOPMOST,1)
        except:
            pass
    
        # Break the loop after the first successful scan
        key=cv2.waitKey(1) & 0xFF
        if key == ord('q') or key==27:
            keep_window_open = False        

        if result is not None:
            break
    
        code = cv2.waitKey(10)
        if code == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

    return result

def extract_barcode():
    barcode_value=scan()
    if is_valid_ean13(barcode_value):
        winsound.Beep(1000,200)
        return [barcode_value,barcode_value[:1:],barcode_value[1:6:],barcode_value[6:7:],barcode_value[7:12:],barcode_value[12::]]
    else:
        winsound.Beep(1000,200)
        winsound.Beep(1000,200)
        extract_barcode()

def is_valid_ean13(barcode):
    if len(barcode) != 13 or not barcode.isdigit():
        return False
    
    even_sum = sum(int(barcode[i]) for i in range(0, 12, 2))
    odd_sum = sum(int(barcode[i]) for i in range(1, 12, 2))
 
    total = odd_sum * 3 + even_sum
    check_digit = (10 - (total % 10)) % 10
    
    print(barcode)
    print("Even sum:", even_sum)
    print("Odd sum:", odd_sum)
    print("Total:", total)
    print("Check digit:", check_digit)
 
    return check_digit == int(barcode[-1])
    
    
if __name__=='__main__':
    extract_barcode()