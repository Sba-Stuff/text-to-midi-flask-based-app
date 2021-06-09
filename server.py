# Importing flask module in the project is mandatory
# An object of Flask class is our WSGI application.
from flask import *
import sys
import os
import codecs
from werkzeug import secure_filename
import re
import music21
import random
from textblob import TextBlob
from collections import deque

#TEMPLATE_DIR = os.path.abspath('../templates')
#STATIC_DIR = os.path.abspath('../static')
# app = Flask(__name__) # to make the app run without any
#app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
UPLOAD_FOLDER = 'static/'
ALLOWED_EXTENSIONS = {"txt","wplt"}
app = Flask(__name__,template_folder="template/",static_folder="static/")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

#@app.route('/output/<path:filepath>')
#def stater(filepath):
#    return send_from_directory('output', filepath)

@app.after_request
def add_header(response):
    # response.cache_control.no_store = True
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

def htmloader(text,inputaudio,outputaudio):
    x = ""
    x+="Utterance: <p>"+text+"</p><br>"
    x+="Original:<br>"
    x+="<audio controls>"
    x+="  <source src='"+inputaudio+"' type='audio/"+inputaudio.rsplit('.', 1)[1].lower()+"'>"
    x+="</audio><br>"
    x+="Cloned Utterance:<br>"
    x+="<audio controls>"
    x+="  <source src='"+str(outputaudio)+"' type='audio/wav'>"
    x+="</audio><br>"
    return x

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
def upload_file():
    fil = []
    if request.method == 'POST':
        f = request.files['file']
        if allowed_file(f.filename):
            f.save(UPLOAD_FOLDER+secure_filename("test.txt"))
            fil.append("File uploaded successfully")
            fil.append(UPLOAD_FOLDER+secure_filename(f.filename))
            return fil
        else:
            fil.append("Not An Expected File")
            return fil
@app.route('/',methods=['GET', 'POST'])
def hello_world():
    legoutput = upload_file()
    lig = "This is a demo utterance. This will work when you do not add any utterance."
    if request.method == 'POST':
        tsp = request.form["timesignature"]
        pst = request.form["psen"]
        nst = request.form["nsen"]
        prm = request.form["prythems"]
        textio = str(tsp)+" | "+str(pst)+" | "+str(nst)+" | "+str(prm)
    print(str(lig))
    #return mainpage()
    if str(legoutput)=="None":
        return render_template("index.html",output="Please Upload A Valid File. Dimagh Na Kha.")
    else:

        gft = str(legoutput[1])
        #script_dir = os.path.dirname(__file__)
        #text = codecs.open(os.path.join(script_dir,str(gft)), encoding='utf-8', errors='ignore')
        from generate import generateXML
        major_penta = [0, 2, 4, 7, 9]
        minor_penta = [0, 3, 5, 7,10]
        major = [0, 2, 4, 5, 7, 9, 11]
        aeolian = [0, 2, 3, 5, 7, 8, 10]
        harmonic_minor = [0, 2, 3, 5, 7, 8, 11]
        mixolydian = [0, 2, 4, 5, 7, 9, 10]
        lydian = [0, 2, 4, 6, 7, 9, 11]
        phrygian = [0, 1, 3, 5, 7, 8, 10]
        whole_tone = [0, 2, 4, 6, 8, 10]
        octatonic = [0, 1, 3, 4, 6, 7, 9, 10]
        twelve_tone = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        scales = [major_penta,minor_penta,major,aeolian,harmonic_minor,mixolydian,lydian,phrygian,whole_tone,octatonic,twelve_tone]
        scale_names = ["Major Pentatonic", "Minor Pentatonic", "Diatonic Major","Aeolian", "Harmonic Minor", "Mixolydian", "Lydian", "Phrygian", "Whole Tone","Octatonic","Twelve Tone"]
        time_sig_string = str(tsp)
        positive_scale =[]
        positive_scale = scales[int(pst)]
        negative_scale = []
        negative_scale = scales[int(nst)]
        arr = [x.strip() for x in prm.split(',')]
        new_arr = []
        for i in arr:
            new_arr.append(float(i))
        custom_rhythm = arr
        script_dir = os.path.dirname(__file__)
        text = codecs.open(os.path.join(script_dir,"static/test.txt"), encoding='utf-8', errors='ignore')
        text_string = text.read()
        textsrc = "<b>Uploaded Text File Content:</b></br><p id='contento' name='contento'>"+text_string+"</p></br>";
        generateXML(positive_scale,negative_scale,custom_rhythm)
        soundsrc = '<b>Generated MIDI:</b></br><midi-visualizer type="staff" src="static/test.midi"> </midi-visualizer> <midi-player src="static/test.midi" sound-font visualizer="#section1 midi-visualizer"> </midi-player>'
        return render_template("index.html",output=textsrc+soundsrc)

        #return render_template("index.html",output=htmloader(text,legoutput[1],fpath))
    #return xieon
# main driver function
if __name__ == '__main__':

    # run() method of Flask class runs the application
    # on the local development server.
    app.run()