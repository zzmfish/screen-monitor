#!/usr/bin/python
#encoding=utf-8
import wx
import sys
import time
import socket

def getScreenShot(rect = None):
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
	return memdc

class ConfFrame(wx.Frame):
	def __init__(self, app):

		self.bmpdc = getScreenShot()
		self.size = self.bmpdc.GetSize()

		self.app = app
		self.buffer = None
		self.pos1 = None
		self.pos2 = None
		self.makingRect = False

		wx.Frame.__init__(self, None, -1, 'Setup')
		self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
		self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
		self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
		self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
		self.Bind(wx.EVT_MOTION, self.OnMotion)
		self.Bind(wx.EVT_PAINT, self.OnPaint)

	
	def OnLeftDown(self, event):
		self.makingRect = True
		self.pos1 = event.GetPosition()
		self.pos2 = None

	def OnLeftUp(self, event):
		self.makingRect = False
		self.pos2 = event.GetPosition()
		self.app.rect = (self.pos1[0], self.pos1[1], \
			self.pos2[0], self.pos2[1])
	
	def OnRightDown(self, event):
		self.Close()

	def OnMotion(self, event):
		if self.makingRect:
			self.pos2 = event.GetPosition()
		dc = self.GetDC()
		self.DrawGraph(dc)
	
	def OnPaint(self, event):
		dc = wx.BufferedPaintDC(self, self.GetBuffer())
	
	def OnKeyDown(self, event):
		if event.GetKeyCode() == wx.WXK_ESCAPE:
			self.Close()
	
	def GetDC(self):
		return wx.BufferedDC(wx.ClientDC(self), self.GetBuffer())
	
	def GetBuffer(self):
		if self.buffer == None:
			w, h = self.GetClientSize()
			self.buffer = wx.EmptyBitmap(w, h)
		return self.buffer

	def DrawGraph(self, dc):
		w, h = self.size

		dc.Blit(0, 0, w, h, self.bmpdc, 0, 0)

		msg = 'Please select a rectangle with a mouse!'
		fw, fh = dc.GetTextExtent(msg)
		fx = (w - fw) / 2
		fy = (h - fh) / 2
		dc.SetTextForeground(wx.GREEN)
		dc.DrawText(msg, fx, fy)
		if self.pos1 != None and self.pos2 != None:
			dc.SetPen(wx.RED_PEN)
			dc.SetBrush(wx.TRANSPARENT_BRUSH)
			dc.DrawRectangle(self.pos1[0], self.pos1[1], \
				self.pos2[0] - self.pos1[0], self.pos2[1] - self.pos1[1])

app = wx.App()
frame = ConfFrame(app)
frame.ShowFullScreen(True, wx.FULLSCREEN_ALL)
frame.SetFocus()
app.MainLoop()

rect = app.rect
rectstr = str(rect[0]) + ',' + str(rect[1]) + ',' + str(rect[2]) + ',' + str(rect[3])
print rectstr
file = open('scrmon.conf', 'w')
file.write(rectstr)
file.close()

