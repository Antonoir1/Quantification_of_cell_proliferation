import numpy as np
import tensorflow as tf
from tensorflow import keras
from PIL import *
from PIL import Image
import matplotlib.pyplot as plt
#M=tf.keras.models.load_model("")
C=tf.keras.models.load_model("compteur2_pour_erreur.h5")

#input: a picture
#return a list of 512*512*1 array croped from the picture X and Y
def cutter(img):
	i=np.array(img)
	#print(i.shape)
	s=512
	xreturn=np.empty([0,512,512],dtype=int)
	Y=s
	while Y<i.shape[1]:
		X=s
		while X<i.shape[0]:
			print(X,Y)
			xreturn=np.append(xreturn,[i[X-s:X,Y-s:Y]],axis=0)

			X=X+s
		#ad a way to deal with all size of picture
		Y=Y+s
	

	xreturn=xreturn.reshape(len(xreturn),s,s,1)
	return xreturn,X-512,Y-512 

#input: a array of croped pictures 512*512
#output: a array of pictures with cells anotated
#draw points where the cells are 
def point(im_array):
	p=M.predict(im_array.astype(float))
	return p

#input: a array of croped picture 512*512
#put the picture back in one piece
def glue(p,X,Y):
	p=p.reshape(len(p),512,512)
	imr=np.zeros((X,Y))
	for x in range(int(X/512)):
		for y in range(int(Y/512)):

			imr[x*512:(x+1)*512,y*512:(y+1)*512,]=p[y*int(X/512)+x]
	return imr

#input: a array of croped pictures 512*512
# count the cells in a anotated picture array
def count(prediction_array):
	P=C.predict(prediction_array.astype(float))
	s=0
	for i in range(len(P)):
		s=s+P[i].argmax()

	return s

# call the methode above
def act(img):
	C=cutter(img)
	points=C[0]
	#points=point(points)
	s=count(points)
	final=glue(points,C[1],C[2])
	return final,s
		


img=Image.open("stack1_T1.tif")
print(act(img))