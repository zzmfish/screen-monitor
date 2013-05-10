#!/usr/bin/python
import wx
import sys
import time
import socket
import thread
import config
from common import *

old_shot = None
new_shot = None

class TaskBarIcon(wx.TaskBarIcon):
  TBMENU_SETUP = wx.NewId()
  TBMENU_CLOSE = wx.NewId()
  state = None

  def __init__(self, frame):
    wx.TaskBarIcon.__init__(self)
    self.frame = frame
    self.SetIcon(load_icon(IMAGE_CONNECTED), APP_NAME)
    self.Bind(wx.EVT_MENU, self.OnTaskBarClose, id=self.TBMENU_CLOSE)

  def CreatePopupMenu(self):
    menu = wx.Menu()
    menu.Append(self.TBMENU_SETUP, "Setup...")
    menu.Append(self.TBMENU_CLOSE, "Close")
    return menu

  def OnTaskBarClose(self, event):
    wx.CallAfter(self.frame.Close)

class Frame(wx.Frame):
  monitor_rect = None

  def __init__(self):
    file = open('scrmon.conf', 'r')
    rectstr = file.readline()
    rectstr = rectstr.split(',')
    self.monitor_rect = (int (rectstr[0]), int (rectstr[1]), int (rectstr[2]), int (rectstr[3]))
    log('The screen rect to monitor is ' + str(self.monitor_rect))

    wx.Frame.__init__(self, None, -1, 'scrmon-client')
    self.tbicon = TaskBarIcon(self)
    self.Bind(wx.EVT_CLOSE, self.OnClose)
    self.Bind(wx.EVT_IDLE, self.OnIdle)
  
  def OnClose(self, event):
    self.tbicon.Destroy()
    self.Destroy()

  def OnIdle(self, event):
    global new_shot
    if not new_shot:
      new_shot = get_screen_shot(self.monitor_rect)

class App(wx.App):
  def OnInit(self):
    self.frame = Frame()
    self.frame.Hide()
    self.SetTopWindow(self.frame)
    return True

def wakeup_timer():
  global old_shot
  global new_shot
  while True:
    log('Connecting to (%s, %d)' % (config.server_host, config.server_port))
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
      try:
        sock.connect((config.server_host, config.server_port))
        break
      except:
        time.sleep(1)

    log('OK')
    while True:
      try:
        f = sock.makefile('rw')
        cmd = recv_line(f)
        if cmd == 'screenshot':
          new_shot = None
          while True:
            wx.WakeUpIdle()
            time.sleep(0.1)
            if new_shot:
              break
          if new_shot != old_shot:
            send_data(f, new_shot)
          else:
            send_data(f, '')
          old_shot = new_shot
        else:
          sys.exit(0)
        f.close()
      except:
        sock.close()
        break
  sock.close()

app = App()
thread.start_new_thread(wakeup_timer, ())
app.MainLoop()
