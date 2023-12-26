from flask import Flask
from flask import request, render_template
import os
import imutils
import cv2
from PIL import Image
from skimage.metrics import structural_similarity
from src.exception import CustomException
import sys
from src.logger import logging

app = Flask(__name__)

#file config
app.config['INITIAL_FILE_UPLOADS'] = os.path.join('static', 'uploads')
app.config['EXISTING_FILE'] = os.path.join('static', 'original')
app.config['GENERATED_FILE'] = os.path.join('static', 'generated')


@app.route("/", methods = ['GET', 'POST'])
def index():
    if request.method=='GET':
        logging.info("Get method called")
        return render_template("index.html")
    
    
    if request.method=="POST":
        try:
            logging.info("Post called called")
            file_upload = request.files['file_upload']
            file_name = file_upload.filename
            logging.info("The file has been loaded through the html page")

            #resize the uploaded image
            uploaded_file = Image.open(file_upload).resize(size=(250, 160))
            logging.info("The uploaded file has been resized to (250, 160)")
            uploaded_file = uploaded_file.convert("RGB")
            logging.info("The file has been converted into RGB by removing the channel Alpha")
            uploaded_file.save(os.path.join(app.config['INITIAL_FILE_UPLOADS'], 'image.jpg'))
            logging.info("The resized image has been successfully saved to the upload directory")

            #resize the original file
            original_file = Image.open(os.path.join(app.config['EXISTING_FILE'], 'image.jpg')).resize(size=(250, 160))
            logging.info("The original image saved locally has been resized to (250, 160)")
            original_file = original_file.convert("RGB")
            logging.info("The file has been converted into RGB by removing the channel Alpha")
            original_file.save(os.path.join(app.config['EXISTING_FILE'], 'image.jpg'))
            logging.info("The resized image has been successfully saved to the original directory")

            # read the original and uploaded images
            original = cv2.imread(os.path.join(app.config['EXISTING_FILE'], 'image.jpg'))
            tampered = cv2.imread(os.path.join(app.config['INITIAL_FILE_UPLOADS'], 'image.jpg'))
            logging.info("Both original and uploaded images have been read in an array form using Opencv")

            # convert it into gray scale images
            original_gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
            logging.info("Original image array has been successfully converted into gray scale image array")
            tampered_gray = cv2.cvtColor(tampered, cv2.COLOR_BGR2GRAY)
            logging.info("Tampered image array has been successfully converted into gray scale image array")

            # calculate the score
            score, diff = structural_similarity(original_gray, tampered_gray, full=True)
            diff = (diff * 255).astype("uint8")
            logging.info("Structural Similarity Index calculation has been initiated.")
            
            # get threshold and countours
            thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
            logging.info("The threshold image values has been successfully calculated")
            countrs = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            countrs = imutils.grab_contours(countrs)
            logging.info("The countours of the images has been successfully calculated")

            for c in countrs:
                (x, y, h, w) = cv2.boundingRect(c)
                cv2.rectangle(original, (x, y), (x+w, y+h), (0, 0, 255), 2)
                cv2.rectangle(tampered, (x, y), (x+w, y+h), (0, 0, 255), 2)
            logging.info("The countours on the images has been successfully drawn")
            
            cv2.imwrite(os.path.join(app.config['GENERATED_FILE'], 'original_image.jpg'), original)
            cv2.imwrite(os.path.join(app.config['GENERATED_FILE'], 'tampered_image.jpg'), tampered)
            cv2.imwrite(os.path.join(app.config['GENERATED_FILE'], 'threshold_image.jpg'), thresh)
            cv2.imwrite(os.path.join(app.config['GENERATED_FILE'], 'difference_image.jpg'), diff)
            logging.info("The image difference of original and tampered has been successfully saved in generated directory")
            logging.info("The Structural Similary index has been successfully calculated")
            pred_score = round(score * 100, 2)
            if pred_score > 80:
                result = "The image is original"
            elif pred_score > 50:
                result = "The image seemes to be original with a need of human inspection"
            else:
                result = "The image is tampered"
            return render_template('index.html', pred = f"{pred_score}% similarity", result = result)



        except Exception as e:
            raise CustomException(e, sys)


if __name__=="__main__":
    app.run(debug=True)