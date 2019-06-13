#!/usr/bin/env python
"""
This is a tool to record changes to an scad file to produce a series of
images or an animated gif showing the progress of a model over time.
Here's a typical workflow:

1) Create an scad file. (Done in OpenSCAD graphical interface).

2) Start recording that scad file.
  python recordscad.py record -in my_model.scad -r recording.zip

3) Create your model. Every time you save, a snapshot is recorded into
   recording.zip

4) Generate images from your recording.
  mkdir my_model_imgs
  python recordscad.py gen_imgs -r recording.zip -imgs my_model_imgs

5) Compile those images into a gif.
  python recordscad.py gen_gif -imgs my_model_imgs -gif creating_my_model.gif
"""
import os
import subprocess
import os.path
import zipfile
import time
import argparse
import tempfile
import shutil
try:
  import imageio
except:
  print "Warning - imageio not installed. Will be unable to generate gifs."

def fileescape(f):
  return "'" + f.replace("'", "'\\''") + "'"

class Recorder:
  def __init__(self, **kwargs):
    self.tmp_dir = kwargs.get('tmp_dir')
    self.watched_file = kwargs.get('watched_file', None)
    self.output_zip = kwargs.get('output_zip', None)
    self.img_dir = kwargs.get('img_dir', None)
    self.gif_file = kwargs.get('gif_file', None)
    self.openscad_bin = kwargs.get('openscad_bin', "openscad")
    self.openscad_args = kwargs.get('openscad_args', \
      "--autocenter --colorscheme='Starnight' -q")

  def store_copy(self):
    with zipfile.ZipFile(self.output_zip, 'a', zipfile.ZIP_DEFLATED) as zf:
      timestamp = os.path.getmtime(self.watched_file)
      newname = '{:016d}.scad'.format(int(timestamp*1000))
      if newname not in zf.namelist():
        zf.write(self.watched_file, newname)

  def print_copies(self):
    with zipfile.ZipFile(self.output_zip, 'r', zipfile.ZIP_DEFLATED) as zf:
      for newname in zf.namelist():
        print newname

  def export_imgs(self):
    tmp_file = os.path.join(self.tmp_dir, "tmp.scad")
    with zipfile.ZipFile(self.output_zip, 'r', zipfile.ZIP_DEFLATED) as zf:
      for name in zf.namelist():
        with open(tmp_file, 'wb') as tf:
          tf.write(zf.read(name))
        timestamp,_ = os.path.splitext(name)
        img_path = os.path.join(self.img_dir, "{}.png".format(timestamp))
        tmp_img_path = os.path.join(self.tmp_dir, "{}.png".format(timestamp))
        cmd = " ".join([
          fileescape(self.openscad_bin),
          fileescape(tmp_file),
          '-o', fileescape(tmp_img_path),
          self.openscad_args
        ])
        print cmd
        os.system(cmd)
        shutil.move(tmp_img_path, img_path)

  def start_recording(self):
    print "Press ctrl-c to stop."
    while True:
      self.store_copy()
      time.sleep(5)

  def generate_gif(self):
    src_files = [f for f in os.listdir(self.img_dir)]
    src_files = [os.path.join(self.img_dir, f) for f in src_files]
    src_files = [f  for f in src_files if os.path.isfile(f)]
    src_files = sorted(src_files)
    durations = [0.1]*(len(src_files)-1)+[5]
    image = None
    with imageio.get_writer(self.gif_file, mode='I', \
        duration=durations, subrectangles=True) as writer:
      for src_file in src_files:
        image = imageio.imread(src_file)
        writer.append_data(image)

parser = argparse.ArgumentParser( \
  description='A tool for recording changes in an OpenSCAD file over time.')
parser.add_argument('action', choices=['record', 'ls', 'gen_imgs', 'gen_gif'], \
  metavar='action', \
  help='Which action to take. '+\
  '\'record\' will poll from the input scad file (-in) '+\
  'and save a copy every time that file changes to the record (-r). '+\
  '\'ls\' will list the content of the record (-r). '+\
  '\'gen_imgs\' will export the contents of of the record (-r) to the '+\
  'image directory (-imgs). '+\
  '\'gen_gif\' will compile the contents of the image directory (-imgs) '+\
  'into an animated gif (-gif).')
parser.add_argument('-in', nargs='?', metavar='input_scad', \
  help='The path to the model file which needs to be watched. '+\
  'For example: \'my_model.scad\'')
parser.add_argument('-r', nargs='?', metavar='recording', \
  help='The zip file into which the scad model snapshots are stored. '+\
  'For example: \'recording.zip\'')
parser.add_argument('-imgs', nargs='?', metavar='image_dir', \
  help='The directory into which images generated from the recording are placed. '+\
  'This directory should already exist, but be empty before gen_imgs is called. '+\
  'For example: \'imgs/\'')
parser.add_argument('-gif', nargs='?', metavar='gif', \
  help='The name of the gif file to generate from the images in -imgs. '+\
  'For example: \'making_of_my_model.gif\'')
parser.add_argument('-openscad_bin', nargs='?', metavar='openscad_bin', \
  default='openscad', \
  help='The path to the binary used to run the openscad command line tool to '+\
  'generate images. '+\
  'Default: \'openscad\'')
parser.add_argument('-openscad_args', nargs='?', metavar='openscad_args', \
  default="-q --autocenter --colorscheme='Starnight'", \
  help='The args used when running openscad to generate images. '+\
  'Default: "-q --autocenter --colorscheme=\'Starnight\'"')
args = vars(parser.parse_args())

tmp_dir = tempfile.mkdtemp()
try:
  # Verify args
  if args['in'] is not None and not os.path.isfile(args['in']):
    raise Exception("The file '"+args['in']+"' does not exist.")
  if args['imgs'] is not None and not os.path.isdir(args['imgs']):
    raise Exception("The directory '"+args['imgs']+"' does not exist.")

  # Create recorder
  recorder_args = {
    'tmp_dir': tmp_dir,
    'watched_file': args['in'],
    'output_zip': args['r'],
    'img_dir': args['imgs'],
    'gif_file': args['gif'],
    'openscad_bin': args['openscad_bin'],
    'openscad_args': args['openscad_args']
  }
  recorder = Recorder(**recorder_args)

  # Perform recorder action
  action = args['action']
  if action == 'record':
    recorder.start_recording()
  elif action == 'ls':
    recorder.print_copies()
  elif action == 'gen_imgs':
    recorder.export_imgs()
  elif action == 'gen_gif':
    recorder.generate_gif()
finally:
  shutil.rmtree(tmp_dir)
