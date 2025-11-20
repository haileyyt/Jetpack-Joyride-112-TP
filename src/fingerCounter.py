import cv2
import mediapipe as mp
import threading

from collections import deque, Counter

class FingerCounter:
    def __init__(self):
        self.fingerNumber = None  # storing current finger count
        self.running = True
        self.counts = deque(maxlen=10)  # to store last 10 counts for averaging

        #https://www.geeksforgeeks.org/multithreading-python-set-1/ 
        self.thread = threading.Thread(target=self.countFingers, daemon=True)
        self.thread.start()

    def countVisibleFingers(self, handLandmarks, handLabel):
        fingerTips = [8, 12, 16, 20] # index, middle, ring, pinky tip
        fingerCount = 0

        #https://mediapipe.readthedocs.io/en/latest/solutions/hands.html 
        landmarks = handLandmarks.landmark
        for tip in fingerTips:
            if landmarks[tip].y < landmarks[tip - 2].y:
                fingerCount += 1
        # Detect thumb separately

        if handLabel == 'right':
            if landmarks[4].x < landmarks[3].x:
                fingerCount += 1
        else:
            if landmarks[4].x > landmarks[3].x:
                fingerCount += 1
        return fingerCount
    # Function to count fingers using webcam

#https://www.geeksforgeeks.org/
#creating-a-finger-counter-using-computer-vision-and-opencv-in-python/

    def countFingers(self):
# https://docs.opencv.org/3.4/d8/dfe/
# classcv_1_1VideoCapture.html#a57c0e81e83e60f36c83027dc2a188e80

        cap = cv2.VideoCapture(0)

        mpHands = mp.solutions.hands
        hands = mpHands.Hands(
            model_complexity=0, max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5) # loading hand model
        
        while self.running:
            success, image = cap.read()
            if not success:
                continue

# https://docs.opencv.org/3.4/d8/dfe/
# classcv_1_1VideoCapture.html#a57c0e81e83e60f36c83027dc2a188e80
            image = cv2.flip(image, 1)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = hands.process(image)
            if results.multi_hand_landmarks and results.multi_handedness:
                combined = zip(results.multi_hand_landmarks, 
                               results.multi_handedness)
                for handLandmarks, handedness in combined:
                    handLabel = handedness.classification[0].label.lower()
                    # Count fingers
                    count = self.countVisibleFingers(handLandmarks, handLabel)
                    self.counts.append(count)
                    common = Counter(self.counts).most_common(1)[0][0]
                    self.fingerNumber = common
            else:
                self.fingerNumber = None
        cap.release()
        cv2.destroyAllWindows()
        hands.close()

    def getFingerCount(self):
        return self.fingerNumber
    
# https://www.geeksforgeeks.org/multithreading-python-set-1/ 
    def stop(self):
        self.running = False
        if self.thread.is_alive():
            self.thread.join(timeout=1.0)  # Give it up to 1 second to clean up

