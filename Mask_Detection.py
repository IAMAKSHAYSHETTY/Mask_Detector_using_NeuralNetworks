# -*- coding: utf-8 -*-
"""Untitled4.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/158tWcWlMjqCUjXC3FUGPvQM3einN4cOV
"""

#This part is only needed while using google colab to mount the google drive
!apt-get install -y -qq software-properties-common python-software-properties module-init-tools
!add-apt-repository -y ppa:alessandro-strada/ppa 2>&1 > /dev/null
!apt-get update -qq 2>&1 > /dev/null
!apt-get -y install -qq google-drive-ocamlfuse fuse
from google.colab import auth
auth.authenticate_user()
from oauth2client.client import GoogleCredentials
creds = GoogleCredentials.get_application_default()
import getpass
!google-drive-ocamlfuse -headless -id={creds.client_id} -secret={creds.client_secret} < /dev/null 2>&1 |grep URL
vcode = getpass.getpass()
!echo {vcode} | google-drive-ocamlfuse -headless -id={creds.client_id} -secret={creds.client_secret}

#mounting google drive
from google.colab import drive
drive.mount('/content/drive')

import os,cv2
os.chdir('/content/drive/My Drive')
dataset = 'data' #or dataset = r''c://' mention the file directory
categories=os.listdir(dataset)

import cv2
import numpy as np
from tensorflow.keras.utils import to_categorical
from sklearn.preprocessing import LabelBinarizer
from sklearn.model_selection import train_test_split

#image preprocessing
im_row, im_col = 100, 100

images = []
target = []

#creating Dataset
for category in categories:
  folder_path = os.path.join(dataset,category)
  for img in os.listdir(folder_path):
    img_path = os.path.join(folder_path,img)
    img = cv2.imread(img_path)
    try:
      gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)#converting to grayscale
      resized = cv2.resize(gray,(im_row, im_col))#resizing the image
      images.append(resized)
      target.append(category)
    except Exception as e:
      print('Exception:',e)

print(target)
images = np.array(images)/255.0
images = np.reshape(images,(images.shape[0],im_row, im_col,1))

#one-hot encoding
lb = LabelBinarizer()
target = lb.fit_transform(target)
target = to_categorical(target)
target = np.array(target)

(trainx, testx, trainy, testy) = train_test_split(images, target, test_size = 0.2 , random_state =0)

from keras.models import Sequential
from keras.layers import Dense,Activation,Flatten,Dropout
from keras.layers import Conv2D,MaxPooling2D

num = 2
batch = 32

#defining cnn model
model = Sequential()

model.add(Conv2D(64,(3,3),input_shape = (im_row, im_col,1)))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size = (2,2)))

model.add(Flatten())
model.add(Dropout(0.5))

model.add(Dense(64,activation='relu'))
model.add(Dense(num,activation='softmax'))

#print(model.summary())
print(trainx.shape)

#training the model
from keras.optimizers import Adam

model.compile(loss = 'categorical_crossentropy',
              optimizer = Adam(lr = 0.001),
              metrics  = ['accuracy'])
epochs = 50
fitted_model  = model.fit(
    trainx,
    trainy,
    epochs = epochs,
    validation_split=0.25)

model.save('detection.h5')

#checking test accuracy
loss, accuracy = model.evaluate(testx, testy)
print('test accuracy: ', accuracy * 100)

#testing the model result
index1 = 1
index2 = 1
preds = model.predict(testx) #WE CAN CHECK FOR ANY IMAGE BY MENTIONING THE IMAGE PATH HERE
#print(preds)
#print('shape of preds: ', preds.shape)
print(categories[int(preds[index1][index2])])



