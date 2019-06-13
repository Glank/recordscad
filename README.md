# RecordSCAD

This is a tool to record changes to an scad file to produce a series of
images or an animated gif showing the progress of a model over time.
Here's a typical workflow:

1) Create an scad file. (Done in OpenSCAD graphical interface).

2) Start recording that scad file.

~~~
  python recordscad.py record -in my_model.scad -r recording.zip
~~~

3) Create your model. Every time you save, a snapshot is recorded into
   recording.zip

4) Generate images from your recording.

~~~
  mkdir my_model_imgs
  python recordscad.py gen_imgs -r recording.zip -imgs my_model_imgs
~~~

5) Compile those images into a gif.

~~~
  python recordscad.py gen_gif -imgs my_model_imgs -gif creating_my_model.gif
~~~

## Example:

![Example](example.gif)

## Install Notes:

This tool has been tested on python version 2.7.10. It's not likely to work with
python 3.

This tool requires the python 'imageio' library in order to generate gifs,
but will run without it. It can be found [here](https://pypi.org/project/imageio/).
