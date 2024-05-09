from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash # to hash the password
from . import db   ##means from __init__.py import db
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash


auth = Blueprint('auth', __name__)

#-------------------------------login ----------------------------
@auth.route('/login', methods=['GET', 'POST'])
# the log in page 
def login():
    # if it is a post request 
    if request.method == 'POST':
        email = request.form.get('email') # get email 
        password = request.form.get('password') # get password
       # cfind the user in the user database by email
        user = User.query.filter_by(email=email).first()
        if user:
            # check the password 
            if check_password_hash(user.password, password):
                # display success message at the top 
                flash('Log in successfully', category='success')
                login_user(user, remember=True)# store in the flask session in the server
                # take to the home 
                return redirect(url_for('views.home'))
            else:
                # display error message 
                flash('Incorrect password', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user) # pass the user variable 

#---------------------------------log out -------------------------------------
@auth.route('/logout')
# the log out page 
@login_required
def logout():
    logout_user()
    # direct to the login page 
    return redirect(url_for('auth.login'))

# sign in ------------------------------------------------------------------
@auth.route('/sign-up', methods=['GET', 'POST'])
# the sign up page 
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        # check if the infomation is in the correct format 
        if user: # email already used and signed in 
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif password1 != password2:
            flash('Passwords entered are different.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
      # correct email and password entered
        else:
            # create a new user and hash the password save in User database
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(
                password1, method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit() # update the database
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            # direct to the home page 
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)


###########################################volume control ######################################
import cv2
import time
import numpy as np
import mediapipe as mp
import math
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
############################

class handDetector():
    def __init__(self, mode = False, maxHands = 2, model_complexity=1, detectionCon = 0.5, trackCon = 0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.model_complexity = model_complexity
        self.detectionCon = detectionCon
        self.trackCon = trackCon
        # initialization
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands,self.model_complexity, self.detectionCon, self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils  # to draw lines on the hands

    def findHands(self, img ,draw = True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # covert to RGB
        self.results = self.hands.process(imgRGB)
        # print(results.multi_hand_landmarks)
        if self.results.multi_hand_landmarks:
            # for each hands
            for handLms in self.results.multi_hand_landmarks:
                # only draw if we asked it to draw
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)  # draw
        return img
    def findPosition(self, img, handNo = 0, draw = True):
        lmList =[]
        # if there are hands
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate (myHand.landmark):
                # print(id, lm) -> in ratio form
                # we convert them by timing the height, width
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id,cx,cy])# add the position to the list
        return lmList


def startcontrol():
    wCam, hCam = 640,480
    cap = cv2.VideoCapture(0)
    # adjust the size of the video
    cap.set(3, wCam)
    cap.set(4,hCam)
    pTime = 0
    # create the detector
    # pycaw -> to adjust the volume !
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = interface.QueryInterface(IAudioEndpointVolume) # access the volumn?
    #volume.GetMute()
    #volume.GetMasterVolumeLevel()
    volRange = volume.GetVolumeRange()

    minVol = volRange[0]
    maxVol = volRange[1]

    detector = handDetector(detectionCon=0.8) # we want to make sure that this is really a hand

    while True:
        success, img = cap.read()
        img = detector.findHands(img)
        # position
        lmList = detector.findPosition(img, draw = False)
        if len(lmList) !=0:
            x1,y1 = lmList[4][1], lmList[4][2]
            x2, y2 = lmList[8][1], lmList[8][2]
            cv2.circle(img, (x1,y1), 15, (255,0,255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
            # draw a line between these two point
            cv2.line(img, (x1,y1), (x2,y2), (255,0,255), 3)
            # find the midpoint
            cx= (x1+ x2)//2
            cy = (y1 + y2)//2
            cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)
            length = math.hypot(x2 - x1, y2 - y1)

            # hand range 20 - 220
            #Volume range - 65 - 0
            vol = np.interp(length, [20, 220], [minVol, maxVol])
            print(vol)
            volume.SetMasterVolumeLevel(vol, None)  # 0 for 100 !
        # show fps
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        cv2.putText(img, str(int(fps)), (40, 70), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 3)
        cv2.imshow("Img", img)
        cv2.waitKey(1)
        # click q to quit 
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    # get out 
    cap.release()
    cv2.destroyAllWindows()

@auth.route('/start_volume_control', methods=['POST'])
@login_required
# the function 
def start_volume_control():
    if request.method == 'POST':
        # Start the volume control program only if the button is clicked
        startcontrol()
       