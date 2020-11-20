#!/usr/bin/env python
# -*- coding: utf-8 -*-

import modules.hashfile
import modules.osapi
import sys
import re
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QListWidget
from PyQt5 import uic
"""
COSAS PARA MEJORAR:
-Desactivar botones cuando realiza la busqueda (para no joder con el servidor)
-
"""


class APIdata:
	login_data = modules.osapi.ConnectAPI()
	search_data = None
	language = {"Español": "spa", "Inglés": "eng"}

#Clase heredada de QMainWindow (Constructor de ventana)
class Window(QMainWindow):
	#Variables flag para determinar que metodo de busqueda se utilizo y 
	#asi descargar el subtitulo de distinta manera
	name_flag = False
	hash_flag = False

	#Constructor de Clase
	def __init__(self):
		#Iniciar el objeto QMainWindow
		QMainWindow.__init__(self)
		#Cargar config del archivo .ui en el objeto
		uic.loadUi("mainwindow.ui",self)
		self.OpenBtt.clicked.connect(self.openDialog)
		self.QuitBtt.clicked.connect(self.quitDialog)
		self.NameSearchBtt.setEnabled(False)
		self.HashSearchBtt.setEnabled(False)
		self.HashSearchBtt.clicked.connect(self.hashSearchSub)
		self.NameSearchBtt.clicked.connect(self.nameSearchSub)
		self.DownloadBtt.clicked.connect(self.downSub)
		self.lineName.textChanged.connect(self.disableButtons)
		self.lineSeason.textChanged.connect(self.disableButtons)
		self.lineEpisode.textChanged.connect(self.disableButtons)
		self.lineFilename.textChanged.connect(self.disableButtons)

	def disableButtons(self):
		#Para desactivar Boton de busqueda por Nombre
		#if (self.lineName.text() == "" or self.lineSeason.text() == "" or self.lineEpisode.text() == ""):
		if (self.lineName.text() == ""):
			self.NameSearchBtt.setEnabled(False)
		else:
			self.NameSearchBtt.setEnabled(True)
		#Para desactivar Boton de busqueda por Hash
		if (self.lineFilename.text() == ""):
			self.HashSearchBtt.setEnabled(False)
		else:
			self.HashSearchBtt.setEnabled(True)
	def openDialog(self):
		#Abrir cuadro de dialogo para buscar archivo, con extensiones predefinidas
		fname = QFileDialog.getOpenFileName(self, 'Abrir archivo', '.',
								 'Video Files (*.avi *.mkv *.mp4 *.mov *.mpg *.wmv)')
		if fname:
			self.lineFilename.setText(fname[0])
	
	def quitDialog(self):
		#Desconectar del servidor de API y salir del programa al apretar Cerrar
		modules.osapi.DisconnectAPI(APIdata.login_data)
		sys.exit()

#Debo desactivar botones mientras hace la busqueda	

	#Metodo de busqueda de Hash
	def hashSearchSub(self):
		Window.name_flag = False
		Window.hash_flag = True
		self.HashSearchBtt.setEnabled(False)
		self.NameSearchBtt.setEnabled(False)
		self.lstSub.clear()	#Limpia la lista de Subtitulos en caso de que hagan mas de una busqueda
		name = self.lineFilename.text()
		if name:
			moviehash, moviesize = modules.hashfile.hashFile(name)
			APIdata.search_data = modules.osapi.SearchAPI(moviehash,
														  moviesize,
														  APIdata.login_data,
														  APIdata.language[self.LangBox.currentText()])
			self.lstSub.addItems(modules.osapi.ShowSubs(APIdata.search_data))
			if self.lstSub.count() == 0:
				self.lbl6.setText("No se encontraron subtitulos.")
		self.HashSearchBtt.setEnabled(True)
		self.NameSearchBtt.setEnabled(True)
#Debo bloquear si no hay campos		

	#Metodo de busqueda por Nombre
	def nameSearchSub(self):
		Window.name_flag = True
		Window.hash_flag = False
		self.lstSub.clear()
		#print("Aca:--><--".format(self.lineSeason.text()))
		APIdata.search_data = modules.osapi.SearchName(self.lineName.text(),
													   self.lineSeason.text(),
													   self.lineEpisode.text(),
													   APIdata.login_data,
													   APIdata.language[self.LangBox.currentText()]
													   )
		self.lstSub.addItems(modules.osapi.ShowSubs(APIdata.search_data))
		if self.lstSub.count() == 0:
			self.lbl6.setText("No se encontraron subtitulos.")

	#Para guardar el nombre del archivo
	#Deberia ir en otra clase
	def movieName(self, movie):
		movie_match = re.match("^(.+)\..+$", movie)
		movie_name = movie_match.group(1)
		return movie_name #string

	#Metodo para descargar el subtitulo y  guardarlo donde corresponda
	def downSub(self):
		if self.lstSub.currentItem(): #si hay un item seleccionado, se descarga
			subindex = self.lstSub.currentRow()
			#Si se busco por nombre, activa name_flag, si se busca por hash, activa hash_flag
			if Window.name_flag:
				sub_file_name = self.lstSub.currentItem().text()
			elif Window.hash_flag:
				sub_file_name = self.movieName(self.lineFilename.text())
			if modules.osapi.DownSubs(APIdata.search_data, subindex, sub_file_name,APIdata.login_data):
				self.lbl6.setText("Subtitulo descargado")
			else:
				self.lbl6.setText("Error")
		else:
			self.lbl6.setText("No elegiste un subtitulo")

#instancia para iniciar aplicacion
app = QApplication(sys.argv)
#Crear objeto de la clase
_window = Window()
#Mostrar ventana
_window.show()
#Ejecutar aplicacion
app.exec_()
