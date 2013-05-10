#!/usr/bin/python
#encoding=utf-8
import wx
import StringIO

STATE_CONNECTED = 0
STATE_DISCONNECTED = 1

IMAGE_CONNECTED = 'images/connected.png'
IMAGE_DISCONNECTED = 'images/disconnected.png'

APP_NAME = 'Screen Monitor'

MODE_SERVER = 0
MODE_CLIENT = 1

def load_icon(file_name):
  image = wx.Image(file_name, wx.BITMAP_TYPE_PNG)
  image = image.Scale(22, 22)
  bitmap = wx.BitmapFromImage(image)
  icon = wx.IconFromBitmap(bitmap)
  return icon

def get_screen_shot(rect = None):
  scrdc = wx.ScreenDC()
  memdc = wx.MemoryDC()

  if rect == None:
    size = scrdc.GetSize()
    x = 0
    y = 0
    w = size[0]
    h = size[1]
  else:
    x = rect[0]
    y = rect[1]
    w = rect[2] - rect[0]
    h = rect[3] - rect[1]

  bmp = wx.EmptyBitmap(w, h)
  memdc.SelectObject(bmp)
  memdc.Blit(0, 0, w, h, scrdc, x, y)
  img = bmp.ConvertToImage()
  file = StringIO.StringIO()
  img.SaveStream(file, wx.BITMAP_TYPE_PNG)
  data = file.getvalue()
  return data

def log(msg):
  pass
  #print msg

def send_line(f, line):
  log('Send: ' + line)
  f.write(line + '\n')
  f.flush()

def send_data(f, data):
  log('Send: (%d bytes)' % len(data))
  f.write('%d\n' % len(data))
  f.write(data)
  f.flush()

def recv_line(f):
  line = f.readline()
  line = line.rstrip('\r\n')
  log('Recv: ' + line)
  return line

def recv_data(f):
  line = f.readline()
  line = line.rstrip('\r\n')
  length = int(line)
  if not length:
    return None
  data = f.read(length)
  if len(data) != length:
    log('Error: Expected %d bytes data, but %d bytes received')
    return None
  log('Recv: (%d bytes)' % len(data))
  return data
