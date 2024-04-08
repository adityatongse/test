# importing required libraries 
# webbrowser for opening web.whatsapp.com into the default web browser
# time for freezing the execution of code for n seconds
# keyboard for closing the opened tab and clicking the send button
# randint from random for creating 4 digit OTP value
import webbrowser 
import time
import keyboard
from random import randint

# this method will create the randon OTP value and returns it with the static message
def generate_otp():
    __otp_value=randint(1000,9999)
    return f"Your one time password for login at InvenTree is {__otp_value}"

# this method will open web browser, send the OTP to the registered user and closes the web browser
def send_otp(contact_number,otp_value):
    link=f"https://web.whatsapp.com/send?phone={contact_number}&text={otp_value}"
    webbrowser.open(link)
    time.sleep(15)
    keyboard.press_and_release('enter')
    time.sleep(5)
    # keyboard.press_and_release('alt+f4')

# main method to create the objects and call them
if __name__=='__main__':
    user_contact="+917040233309"
    otp_value=generate_otp()
    print(otp_value)
    send_otp("+917040233309",otp_value)