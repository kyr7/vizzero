from PyQt5 import QtWidgets
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEnginePage
from PyQt5.QtWebEngineWidgets import QWebEngineView


def create_hand_sim_widget(parent=None):

    view = QWebEngineView(parent)
    view.setUrl(QUrl("file://../handjs/index.html"))
    return view

