#!/usr/bin/python
#encoding=utf-8

import os
import sys
import time
import socket
import thread
import time
import config
from common import *

sock = None
conn = None
connfile = None

TBMENU_CLOSE = wx.NewId()
TBMENU_SHOW = wx.NewId()
TBMENU_HIDE = wx.NewId()

class TaskBarIcon(wx.TaskBarIcon):
  state = None

  def __init__(self, frame):
    wx.TaskBarIcon.__init__(self)
    self.frame = frame
    self.normalIcon = load_icon(IMAGE_CONNECTED)
    self.disabledIcon = load_icon(IMAGE_DISCONNECTED)
    self.SetState(STATE_DISCONNECTED)
    self.Bind(wx.EVT_MENU, self.OnTaskBarClose, id=TBMENU_CLOSE)
    self.Bind(wx.EVT_MENU, self.OnTaskBarShow, id=TBMENU_SHOW)
    self.Bind(wx.EVT_MENU, self.OnTaskBarHide, id=TBMENU_HIDE)

  def CreatePopupMenu(self):
    menu = wx.Menu()
    menu.Append(TBMENU_SHOW, "显示")
    menu.Append(TBMENU_HIDE, "隐藏")
    menu.Append(TBMENU_CLOSE, "退出")
    return menu

  def OnTaskBarClose(self, event):
    wx.CallAfter(self.frame.Close)

  def OnTaskBarShow(self, evnet):
    self.frame.Show()

  def OnTaskBarHide(self, evnet):
    self.frame.Hide()

  def SetState(self, state):
    if state == self.state:
      return
    self.state = state
    if state == STATE_CONNECTED:
      self.SetIcon(self.normalIcon, APP_NAME)
    elif state == STATE_DISCONNECTED:
      self.SetIcon(self.disabledIcon, APP_NAME)

class Frame(wx.Frame):
  image = None
  bitmap = None
  mouse_down_pos = None
  frame_pos = None
  last_idle_time = 0.0

  def __init__(self):
    frame_style = wx.STAY_ON_TOP# | wx.NO_BORDER
    wx.Frame.__init__(self, None, -1, '屏幕监视器', style=frame_style, size=(200,100), pos=(100,100))
    self.timer = wx.Timer(self)
    self.timer.Start(config.moniter_interval * 1000)
    self.Bind(wx.EVT_CLOSE, self.OnClose)
    self.Bind(wx.EVT_TIMER, self.OnTimer)
    self.Bind(wx.EVT_PAINT, self.OnPaint)
    self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
    self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
    self.Bind(wx.EVT_MOTION, self.OnMotion)
    self.tbicon = TaskBarIcon(self)
    self.tbicon.SetState(STATE_DISCONNECTED)

    #创建弹出菜单
    menu = wx.Menu()
    menu.Append(TBMENU_HIDE, "隐藏")
    menu.Append(TBMENU_CLOSE, "退出")
    self.popupmenu = menu
    self.Bind(wx.EVT_CONTEXT_MENU, self.OnShowPopup)
    self.Bind(wx.EVT_MENU, self.OnHide, id=TBMENU_HIDE)
    self.Bind(wx.EVT_MENU, self.OnClose, id=TBMENU_CLOSE)
    self.Show()

  def OnShowPopup(self, event):
    pos = event.GetPosition()
    pos = self.ScreenToClient(pos)
    self.PopupMenu(self.popupmenu, pos)

  def OnHide(self, event):
    #self.Hide()
    pass

  def OnClose(self, event):
    self.tbicon.Destroy()
    self.Destroy()

  def OnTimer(self, event):
    global conn,connfile
    if not connfile:
      return
    cur_time = time.time()
    if cur_time - self.last_idle_time < config.moniter_interval:
      return
    self.last_idle_time = cur_time
    try:
      send_line(connfile, 'screenshot')
      self.tbicon.SetState(STATE_CONNECTED)
      data = recv_data(connfile)
      if data:
        stream = StringIO.StringIO(data)
        try:
          image = wx.ImageFromStream(stream)
          app.frame.ShowImage(image)
        except:
          log('Error: Bag image data!!!')
    except: #连接已经失效
      connfile.close()
      connfile = None
      conn.close()
      conn = None
      self.tbicon.SetState(STATE_DISCONNECTED)
      #self.Hide()
      return

  def OnPaint(self, event):
    dc = wx.PaintDC(self)
    if self.image:
      self.bitmap = wx.BitmapFromImage(self.image)
      self.image = None
    if self.bitmap:
      dc.DrawBitmap(self.bitmap, 0, 0, False)
    frame_size = self.GetSize()
    dc.SetPen(wx.BLACK_PEN)
    dc.SetBrush(wx.TRANSPARENT_BRUSH)
    dc.DrawRectangle(0, 0, frame_size[0], frame_size[1])

  def ShowImage(self, image):
    self.image = image
    self.SetSize(image.GetSize())
    self.Show()
    self.Refresh()

  def OnLeftDown(self, event):
    self.frame_pos = self.GetScreenPosition()
    self.mouse_down_pos = event.GetPosition()
    self.mouse_down_pos[0] += self.frame_pos[0]
    self.mouse_down_pos[1] += self.frame_pos[1]

  def OnLeftUp(self, event):
    self.mouse_down_pos = None
    self.frame_pos = None

  def OnMotion(self, event):
    if self.mouse_down_pos and self.frame_pos:
      frame_pos = self.GetScreenPosition()
      mouse_pos = event.GetPosition()
      mouse_pos[0] += frame_pos[0]
      mouse_pos[1] += frame_pos[1]
      x = self.frame_pos[0] + mouse_pos[0] - self.mouse_down_pos[0]
      y = self.frame_pos[1] + mouse_pos[1] - self.mouse_down_pos[1]
      self.SetPosition((x, y))

class App(wx.App):
  def OnInit(self):
    self.frame = Frame()
    self.SetTopWindow(self.frame)
    return True

def connect_thread():
  global sock,conn,connfile
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  log('Binding port %d ...' % config.server_port)
  sock.bind(('', config.server_port))
  sock.listen(1)
  log('Listening ...')
  while True:
    if not connfile:
      conn, addr = sock.accept()
      log('Accepted: (%s:%s)' % (addr[0], addr[1]))
      connfile = conn.makefile()
    time.sleep(1)

app = App()
thread.start_new_thread(connect_thread, ())
app.MainLoop()

if conn:
  conn.close()
if connfile:
  connfile.close()
