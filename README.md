# Quantification of cell proliferation (WARNING: WORK IN PROGRESS)

## Description:

The goal of this project was to make a tool for the researchers (in the cancer cell proliferation) to use. This tool will count the cell population in a given image (.tif or .tiff), and will even track the cell flows over time, if these images are given with a time order and a prefix (ex: Time => Time00, Time01, Time02...). Warning: the time order must be superior or equal to 0.

## Prerequisites

<ul>
<li>Windows 7/8/10</li>
<li>Linux</li>
</ul>

## Prerequisites optional (Run the code directly)

<ul>
<li>python 3 (https://www.python.org)</li>
<li>Qt5 (https://www.qt.io)</Li>
<li>PySide2 (https://wiki.qt.io/Qt_for_Python)</li>
<li>numpy (https://pypi.org/project/numpy)</li>
<li>PIL (https://pypi.org/project/Pillow)</li>
<li>Tensorflow (https://www.tensorflow.org)</li>
<li>Keras (https://keras.io)</li>
</ul>

## Run

To run this project you can enter the following command:
```bash
$ python Cell_Counter.py
```

## Manual

### Prerequisites

<ul>
<li>A folder containing .tiff or .tif images of your cell population</li>
<li>Every images must have the same prefix followed by an integer superior or equal to 0 (ex: prefix = population, images = population0, population1...)</li>
</ul>

### Step 1: Add the path of your images folder

Click on the 'Browse' button and select the folder containing your image (Shortcuts: CTRL+O).

### Step 2: Add the images prefix

Type your images's prefix in the prefix input field.

### Step 3: Launch the processing of the images

Click on the 'Process Data' button to process your images (Shortcut: CTRL+P).

### Step 4: Observe the results

You can observe on the 'Cell population' graph the evolution of this cell population over time. By hovering your mouse on the graph you will see the points's values, and by selecting a part of the graph with the Left click you can zoom in (Left click to zoom out).

You can also observe on the 'Population image' displayer, on each timepoint the number of cells in your population with the buttons on both sides of the image (Shortcuts: CTRL+B = Last image, CTRL+N = Next image).