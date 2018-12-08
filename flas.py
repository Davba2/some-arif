from flask import Flask, render_template, request, Response, redirect, flash, session, url_for, jsonify, json, make_response, send_file
from pymongo import MongoClient
import json
import time
import cv2
from keras import backend as K
from keras.models import Sequential, load_model  # инициализация нейронной сети
from keras.layers import Convolution2D  # конволютион степ. для изображения
from keras.layers import MaxPooling2D
from keras.layers import Flatten
from keras.layers import Dense
from keras.layers import Dropout
import numpy as np
from keras_preprocessing import image
import datetime
from skimage import color
from skimage import io
import os
from keras.utils import np_utils

app = Flask(__name__)
UPLOAD_FOLDER = 'C:\\7 семестр\\Новая папка\\static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

font = cv2.FONT_HERSHEY_SIMPLEX
text = ''
# строка подключения к базе данных на млабе
dmongo = MongoClient('mongodb://localhost:27017/')

db = dmongo['tdatabase']


def vybor_znaka(res):

    prediction = ''
    print(res)
    if res[0][0] > 0.9:
        prediction = '('
    elif res[0][1] > 0.9:
        prediction = ')'
    elif res[0][2] > 0.9:
        prediction = '+'
    elif res[0][3] > 0.9:
        prediction = '-'
    elif res[0][4] > 0.9:
        prediction = '0'
    elif res[0][5] > 0.9:
        prediction = '1'
    elif res[0][6] > 0.9:
        prediction = '2'
    elif res[0][7] > 0.9:
        prediction = '3'
    elif res[0][8] > 0.9:
        prediction = '4'
    elif res[0][9] > 0.9:
        prediction = '5'
    elif res[0][10] > 0.9:
        prediction = '6'
    elif res[0][11] > 0.9:
        prediction = '7'
    elif res[0][12] > 0.9:
        prediction = '8'
    elif res[0][13] > 0.9:
        prediction = '9'
    elif res[0][14] > 0.9:
        prediction = '/'
    elif res[0][15] > 0.9:
        prediction = '*'
    return prediction


@app.route('/')
def gg():
    return render_template("main.html")


@app.route('/file_on', methods=["GET", "POST"])
def cam():
    filee = request.files['file']
    name = "image.png"
    filee.save(name)
    font = cv2.FONT_HERSHEY_SIMPLEX
    text = ''
    clas = Sequential()
    clas = load_model('arif_all_1000na300.hd5')
    frame = cv2.imread("image.png", 1)
    frame2 = frame.copy()
    fr = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    fr = cv2.GaussianBlur(fr, (7, 7), 0)
    blur = cv2.GaussianBlur(fr, (15, 15), 0)
    thresh = cv2.adaptiveThreshold(blur, 255, 1, 1, 11, 2)
    c = cv2.waitKey(1)
    (_, contours, _) = cv2.findContours(
        thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    fg = 0
    somess = 0
    otvet = ''
    zza = []
    pozition = {}
    for cin in contours:
        if cv2.contourArea(cin) > 90:
            # continue
            (x, y, w, h) = cv2.boundingRect(cin)

            if h > 110:
                print("__________")
                print("x-{0}".format(x))
                print("y-{0}".format(y))
                print("h-{0}".format(h))
                print("w-{0}".format(w))
                print("__________")
                bb = frame[y:y+h, x:x+w]
                cv2.imwrite(
                    'fxx{0}.jpg'.format(fg), bb)
                test = image.load_img(
                    path='fxx{0}.jpg'.format(fg), target_size=(45, 45, 1))
                test = image.img_to_array(test)
                test = np.expand_dims(test, axis=0)
                res = clas.predict(test)
                text = vybor_znaka(res)
                otvet = otvet+text
                zza.append(text)
                pozition[x] = text
                print("Пред - {0}".format(text))
                cv2.putText(frame2, text, (x-10, y-15), font,
                            1, (255, 153, 0), 1, cv2.LINE_AA)
                fg += 1
                cv2.rectangle(frame2, (x, y), (x+w, y+h), (0, 255, 0), 3)
    print(otvet)
    print(zza)
    print(pozition)
    print("____")
    stroka = ''
    keys = pozition.keys()
    for k in sorted(keys):
        print(" {0} {1} ".format(k, pozition[k]))
        stroka = stroka+pozition[k]
        print("____")

    print(stroka)
    ot = ''
    try:
        ot = eval(stroka)
    except:
        print('Это не сработало')
    cv2.putText(frame2, str(ot), (10, 25), font,
                1, (155, 153, 50), 1, cv2.LINE_AA)
    cv2.imwrite('static/fxx_out1.jpg', frame2)
    K.clear_session()
    pics = '/static/fxx_out1.jpg'
    
    
    return json.dumps({'src': '/static/fxx_out1.jpg', 'otvet': stroka, 'ot': ot})


@app.route('/delete/<string:name>', methods=['DELETE'])
def delete(name):
    users = db.arif
    print(name)
    output = {}
    co = users.find().sort('dt', -1)
    for a in co:
        print(a)
        if str(a['_id']) == name:
            print('Успех')
            users.remove({'_id': name})

            break
    return json.dumps({'status': 'окей', 'code': 200})


@app.route('/get_db', methods=["GET"])
def get_db():
    users = db.arif
    z = users.find().sort('dt', -1)
    dz = {}
    f = 0
    sto = []
    ot = []
    dat = []
    id_ = []
    for a in z:
        gg = str(f)
        dz[gg] = a['otvet']
        id_.append(a['_id'])
        sto.append(a['stroka'])
        ot.append(a['otvet'])
        dat.append(a['dt'])
        f += 1
    return render_template("db.html", sto=sto, ot=ot, dt=dat, id=id_, f=f)


if __name__ == "__main__":
    app.run(debug=True)

