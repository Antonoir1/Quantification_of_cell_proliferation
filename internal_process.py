import numpy as np
import tensorflow as tf
from tensorflow import keras
from PIL import *
from PIL import Image, ImageOps
import matplotlib.pyplot as plt

M=tf.keras.models.load_model("./models/Unet_1_16.h5")
C=tf.keras.models.load_model("./models/compteur2.h5")

#input: a picture
#return a list of 512*512*1 array croped from the picture X and Y
def cutter(img):
	i=np.array(img)
	xreturn=np.empty([0,512,512],dtype=int)
	Y=int(1+(i.shape[1]-i.shape[1]%512)/512)
	X=int(1+(i.shape[0]-i.shape[0]%512)/512)
	for y in range(Y):
		for x in range(X):
			zero=np.zeros([512,512])
			droite=min((1+x)*512,i.shape[0])
			haut=min((1+y)*512,i.shape[1])
			gauche=droite-512
			bas=haut-512
			xm=512
			ym=512
			if haut%512>0:
				
				bas=haut-haut%512
				ym=haut%512
			if droite%512>0:
				
				gauche=droite-droite%512
				xm=droite%512

			zero[0:xm,0:ym]=i[gauche:droite,bas:haut]
			
			xreturn=np.append(xreturn,[zero],axis=0)
	xreturn=xreturn.reshape(len(xreturn),512,512,1)
	return xreturn,X,Y



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
	
	img=np.zeros([X*512,Y*512])
	for y in range(Y):
		for x in range(X):
			
			img[x*512:(x+1)*512,y*512:(y+1)*512]=p[y*(Y-1)+x]
	return img


#input: a array of croped pictures 512*512
# count the cells in a anotated picture array
def count(prediction_array):
	P=C.predict(prediction_array.astype(float))
	s=0
	for i in range(len(P)):
		s=s+P[i].argmax()

	return s

# call the methode above
def act(img, index):
	C=cutter(Image.open(img))
	points=C[0]
	points=point(points)
	s=count(points)
	final=glue(points,C[1],C[2])
	final = (final*255).astype(np.uint8)

	img_tmp = np.array(Image.open(img).convert("RGB"))
	for i in range(0,final.shape[0]):
		for j in range(0,final.shape[1]):
			if(final[i,j] >= 204):
				img_tmp[i,j][0] = 255
				img_tmp[i,j][1] = 0
				img_tmp[i,j][2] = 0

	img_final = Image.fromarray(img_tmp)
	img_final.save("./tmp/tmp"+str(index)+".tiff")
	return s
		