import os
import numpy as np
from tensorflow import keras
from PIL import Image

try:
	M=keras.models.load_model("./models/Unet_1_16.h5")
	C=keras.models.load_model("./models/compteur2.h5")
except:
	pass

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

#alternative version for count, need the full anotated picture as a input
def count2(img):
	#filtre:
	filtre=0.8
	for x in range(img.shape[0]):
		for y in range(img.shape[1]):
			if img[x][y]<filtre:
				img[x][y]=0 
	s=sum(img)
	s=sum(s)
	s=int(s/(12*12))
	return s 

# call the methode above
def act(img, index):
	#8-bits grayscale
	if(Image.open(img).mode == "L"):
		img = Image.open(img)
	#8-bits color
	elif(Image.open(img).mode == "RGB"):
		img = Image.open(img).convert("RGB")
	#32-bit float
	elif(Image.open(img).mode == "F"):
		arr = np.array(Image.open(img))
		arr = arr*255
		arr = arr.astype(np.uint8)
		img = Image.fromarray(arr)
	#16-bit signed int
	elif(Image.open(img).mode == "I"):
		arr = np.array(Image.open(img))
		addi = 0
		if(np.amin(arr) < 0):
			addi = 32768
		arr = (arr+addi)*(255/65535)
		arr = arr.astype(np.uint8)
		img = Image.fromarray(arr)

	C=cutter(img)
	points=C[0]
	points=point(points)
	final=glue(points,C[1],C[2])
	s=count2(final)


	img_tmp = np.array(img.convert("RGB"))
	for i in range(0,img_tmp.shape[0]):
		for j in range(0,img_tmp.shape[1]):
			if(final[i,j] >= 0.8):
				img_tmp[i,j][0] = 255
				img_tmp[i,j][1] = 0
				img_tmp[i,j][2] = 0

	img_final = Image.fromarray(img_tmp)
	img_final.save("./tmp/tmp"+str(index)+".tiff")
	return s
		