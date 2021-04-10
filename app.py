import sys
import os
import time
import random as rnd
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib
import tkinter as tk
from tkinter import filedialog

matplotlib.use('Qt5Agg')

test_graph = [[1, 2], [1, 3], [2, 5], [2, 3], [5, 4], [1, 5], [3, 6], [7, 8], [8, 2], [1, 5], [4, 7], [7, 6]]
INF = 1e10


class Graph:
    def __init__(self, n=0, m=0, ordered=False):
        self.edges = m
        self.vertices = n
        self.ordered = ordered
        self.adjacency_list = []

    def add_edge(self, u, v, weight=1):
        u -= 1
        v -= 1
        self.adjacency_list[u].append([v, weight])
        if not self.ordered:
            self.adjacency_list[v].append([u, weight])

    def set_edges(self, n):
        self.edges = n

    def set_vertices(self, n):
        self.vertices = n

    def create(self):
        for i in range(self.vertices):
            self.adjacency_list.append([])

    def add_adj_list(self, list_):
        self.adjacency_list = list_
        self.vertices = len(self.adjacency_list)
        self.edges = 0
        for i in self.adjacency_list:
            self.edges += len(i)
        self.edges //= 2

    def add_edge_list_unweighted(self, edges):
        n = 0
        for i in edges:
            n = max(n, i[0], i[1])
        self.adjacency_list.clear()
        self.vertices = n
        self.edges = len(edges)
        for _ in range(self.vertices):
            self.adjacency_list.append([])
        for edge in edges:
            self.add_edge(edge[0], edge[1])

    def dijkstra(self, from_, to_):
        global INF

        from_ -= 1
        to_ -= 1

        dist = [INF] * self.vertices
        used = [False] * self.vertices
        p = [-1] * self.vertices

        dist[from_] = 0

        for _ in range(self.vertices):
            v = -1
            for vertice in range(self.vertices):
                if not used[vertice] and (v == -1 or dist[vertice] < dist[v]):
                    v = vertice
            if dist[v] == INF:
                break
            used[v] = True
            for node in self.adjacency_list[v]:
                destination = node[0]
                w = node[1]
                if dist[v] + w < dist[destination]:
                    dist[destination] = dist[v] + w
                    p[destination] = v
        if dist[to_] != INF:
            return dist[to_], self.get_path(p, from_, to_)
        return -1, -1

    def get_path(self, p, from_, to_):
        path = []
        current_v = to_
        while current_v != from_:
            path.append(current_v + 1)
            current_v = p[current_v]
        path.append(from_ + 1)
        return path[::-1]

    def dfs(self):
        used = [False] * self.vertices
        way = []
        for i in range(self.vertices):
            if not used[i]:
                k = []
                self.dfs_rec(i, k, used)
                way.append(k)
        return way

    def dfs_rec(self, u, array, used):
        array.append(u + 1)
        used[u] = True
        for v in self.adjacency_list[u]:
            if not used[v[0]]:
                self.dfs_rec(v[0], array, used)

    def get_edge_list(self):
        res = []
        c = 1
        for node in self.adjacency_list:
            for i in node:
                res.append([c, i[0] + 1])
            c += 1
        return res


maingraph = Graph()


class GraphVisualization:
    def __init__(self):
        self.visual = []

    def addEdge(self, a, b):
        temp = [a, b]
        self.visual.append(temp)

    def by_graph(self, gr):
        self.visual = gr.get_edge_list()

    def set_graph(self, gr_example):
        self.visual = gr_example

    def visualize(self):
        plt.clf()
        Gr = nx.Graph()
        Gr.add_edges_from(self.visual)
        u = nx.draw_networkx(Gr, node_color="#00b4d9")

        plt.savefig("imageee.jpg", dpi=120)

    def visualize_colored(self, chosen):
        t = []
        for i in self.visual:
            if i in chosen or i[::-1] in chosen:
                t.append('red')
            else:
                t.append('green')
        Gr = nx.Graph()
        Gr.add_edges_from(self.visual)
        u = nx.draw_networkx(Gr, node_color="#00b4d9", edge_color=t)

        plt.savefig("imageee.jpg", dpi=120)


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class HyperlinkLabel(QLabel):
    def __init__(self, x, y, parent=None):
        super().__init__()
        self.setStyleSheet('font-size: 20px')
        self.setOpenExternalLinks(True)
        self.setParent(parent)
        self.move(x, y)


class AddGraphApplication(QMainWindow, QWidget):
    def __init__(self):
        super(AddGraphApplication, self).__init__()
        self.resize(600, 600)
        self.setWindowTitle("New graph keyboard input")
        self.initUI()

    def initUI(self):
        self.new_graph_v = -1
        self.new_graph_e = -1
        self.new_graph = Graph()
        # Getting main parameters
        self.ask_vertices()
        self.ask_edges()

        # Input of graph
        self.ask_input_type()

        self.show()

    def ask_input_type(self):
        self.input_graph = QTextEdit(self)
        self.input_graph.setGeometry(8, 150, 400, 400)

        asks = "Which type of graph's input you would prefer to use?"
        self.chose_question = QLabel(asks, self)
        self.chose_question.setGeometry(5, 90, 310, 20)

        # Chosing input type
        self.chose_type = QComboBox(self)
        self.chose_type.setGeometry(8, 115, 100, 30)
        self.chose_type.addItems(["Edges list", "Adjency matrix"])
        self.chose_type.activated[str].connect(self.type_chosen)
        self.type = -1

        # Set warning
        params_warning = "<font color='red'>Number of edges or vertices is not given</font>"
        self.params_not_given_warning = QLabel(params_warning, self)
        self.params_not_given_warning.setGeometry(8, 150, 300, 20)
        self.params_not_given_warning.hide()

        # Confirm input
        self.confirm_button = QPushButton("Confirm", self)
        self.confirm_button.setGeometry(8, 555, 70, 30)
        self.graph_info = ""
        self.confirm_button.clicked.connect(self.get_text)

    def get_text(self):
        global maingraph
        t = self.input_graph.toPlainText()
        self.type = 1
        if self.check_input(self.type, t):
            if self.type == 1:
                edges = t.split('\n')
                for edge in edges:
                    if edge != '':
                        vv = list(map(int, edge.split(' ')))
                        if len(vv) == 2:
                            self.new_graph.add_edge(vv[0], vv[1])
            else:
                pass
            maingraph = self.new_graph
            self.close()
        else:
            pass

    def check_input(self, t1, text_):
        ''' Bool function'''
        return True
        # Checking algorithm
        if t1 == 1:
            right = True
            t = text_.split('\n')
            for i in t:
                p = i.split(' ')
                if not (len(p) == 2 and p[0].isnumeric() and p[1].isnumeric()):
                    right = False
            if len(t) != self.new_graph_e:
                right = False
            return right
        else:
            right = True
            t = text_.split('\n')
            # later
            return True

    def type_chosen(self, text):
        if text == "Edges list":
            self.type = 1
        else:
            self.type = 2

    def ask_vertices(self):
        """ Creating main widgets """
        self.ask_v = QLabel('Enter number of vertices:', self)
        self.enter_v = QLineEdit(self)
        self.submit_button_v = QPushButton('submit', self)

        # Moving widgets
        self.move_ask(self.ask_v, self.submit_button_v, self.enter_v, 15)

        # Getting vertices of graph
        self.set_submit_button_v()
        self.set_warning_v()

    def ask_edges(self):
        """ Creating main widgets """
        self.ask_e = QLabel('Enter number of edges:', self)
        self.enter_e = QLineEdit(self)
        self.submit_button_e = QPushButton('submit', self)

        # Moving widgets
        self.move_ask(self.ask_e, self.submit_button_e, self.enter_e, 50)

        # Getting vertices of graph
        self.set_submit_button_e()
        self.set_warning_e()

    def set_submit_button_e(self):
        self.submit_button_e.setStyleSheet("background-color: #FF4545; border-style: outset; border-radius: 2px")
        self.submit_button_e.clicked.connect(self.submit_btne_pressed)

    def set_submit_button_v(self):
        self.submit_button_v.setStyleSheet("background-color: #FF4545; border-style: outset; border-radius: 2px")
        self.submit_button_v.clicked.connect(self.submit_btnv_pressed)

    def set_warning_e(self):
        """ If edges input was not correct """
        label_text = "<font color='red'>Input is not a number</font>"
        self.warning_e = QLabel(label_text, self)
        self.warning_e.move(400, 50)
        self.warning_e.resize(200, 30)
        self.warning_e.hide()

    def set_warning_v(self):
        """ If vertices input was not correct """
        label_text = "<font color='red'>Input is not a number</font>"
        self.warning_v = QLabel(label_text, self)
        self.warning_v.move(400, 15)
        self.warning_v.resize(200, 30)
        self.warning_v.hide()

    def submit_btnv_pressed(self):
        """ Checks input and sets graph's vertices """
        self.text_v = self.enter_v.text()
        if self.check(self.text_v):
            self.submit_button_v.setStyleSheet("background-color: #88d498; border-style: outset; border-radius: 2px")
            self.new_graph_v = int(self.text_v)
            self.new_graph.set_vertices(self.new_graph_v)
            self.warning_v.hide()
            self.enter_v.setReadOnly(True)
        else:
            self.warning_v.show()
            self.submit_button_v.setStyleSheet("background-color: #FF4545; border-style: outset; border-radius: 2px")

    def submit_btne_pressed(self):
        """ Checks input and sets graph's edges """
        self.text_e = self.enter_e.text()
        if self.check(self.text_e):
            self.submit_button_e.setStyleSheet("background-color: #88d498; border-style: outset; border-radius: 2px")
            self.warning_e.hide()
            self.new_graph_e = int(self.text_e)
            self.new_graph.set_edges(self.new_graph_e)
            self.new_graph.create()
            self.enter_e.setReadOnly(True)
        else:
            self.warning_e.show()
            self.submit_button_e.setStyleSheet("background-color: #FF4545; border-style: outset; border-radius: 2px")

    def move_ask(self, label, button, line, y):
        """ Void function """
        label.resize(200, 20)
        label.move(5, y + 5)
        button.move(275, y)
        line.move(160, y)

    def check(self, text):
        """ bool function """
        return text.isnumeric()

    def get_graph(self):
        return self.new_graph


class InfoApplication(QMainWindow, QWidget):
    def __init__(self):
        super(InfoApplication, self).__init__()
        self.initUI()

    def initUI(self):
        self.resize(450, 205)
        self.setWindowTitle('Основные сведения о графах')

        link_template = '<a href={0}>{1}</a><br><br><a href={2}>{3}</a><br><br><a href={4}>{5}</a><br><br><a href={' \
                        '6}>{7}</a> '
        link1 = 'https://ru.wikipedia.org/wiki/%D0%93%D1%80%D0%B0%D1%84_(' \
                '%D0%BC%D0%B0%D1%82%D0%B5%D0%BC%D0%B0%D1%82%D0%B8%D0%BA%D0%B0) '
        link2 = 'https://ru.wikipedia.org/wiki/%D0%93%D1%80%D0%B0%D1%84_(' \
                '%D0%BC%D0%B0%D1%82%D0%B5%D0%BC%D0%B0%D1%82%D0%B8%D0%BA%D0%B0)#%D0%A1%D0%BF%D0%BE%D1%81%D0%BE%D0%B1' \
                '%D1%8B_%D0%BF%D1%80%D0%B5%D0%B4%D1%81%D1%82%D0%B0%D0%B2%D0%BB%D0%B5%D0%BD%D0%B8%D1%8F_%D0%B3%D1%80' \
                '%D0%B0%D1%84%D0%B0_%D0%B2_%D0%B8%D0%BD%D1%84%D0%BE%D1%80%D0%BC%D0%B0%D1%82%D0%B8%D0%BA%D0%B5 '
        link3 = 'https://ru.wikipedia.org/wiki/%D0%97%D0%B0%D0%B4%D0%B0%D1%87%D0%B0_%D0%BE_%D0%BA%D1%80%D0%B0%D1%82' \
                '%D1%87%D0%B0%D0%B9%D1%88%D0%B5%D0%BC_%D0%BF%D1%83%D1%82%D0%B8'
        link4 = 'https://ru.wikipedia.org/wiki/%D0%9E%D1%81%D1%82%D0%BE%D0%B2%D0%BD%D0%BE%D0%B5_%D0%B4%D0%B5%D1%80%D0' \
                '%B5%D0%B2%D0%BE '
        name1 = 'Основная информация'
        name2 = 'Способы хранения графа в памяти компьютера'
        name3 = 'Поиск кратчайших путей в графе'
        name4 = 'Остовное дерево'
        main_info_label1 = HyperlinkLabel(5, 170, self)
        main_info_label1.move(0, -145)
        main_info_label1.setText(
            link_template.format(
                link1, name1, link2, name2, link3, name3, link4, name4
            )
        )

        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


class MainApplication(QMainWindow, QWidget, QCoreApplication):
    def __init__(self):
        super().__init__()
        self.dialogs = list()
        self.resize(1000, 680)
        self.center()
        self.initUI()

    def link(self, link_str):
        QDesktopServices.openUrl(QUrl(link_str))

    def showButtons(self):
        self.btn1 = QPushButton("Create", self)
        self.btn1.move(850, 46)
        self.btn1.resize(125, 83)
        self.btn1.setFont(QFont("Times", 12, 65, True))

        self.btn2 = QPushButton("Load", self)
        self.btn2.setFont(QFont("Times", 12, 65, True))
        self.btn2.move(700, 46)
        self.btn2.resize(125, 83)

        self.info_button = QPushButton(self)
        self.info_button.setIconSize(QSize(47, 47))
        self.info_icon = QIcon('info.png')
        self.info_button.setIcon(self.info_icon)
        self.info_button.move(20, 42)
        self.info_button.resize(75, 75)
        self.info_button.setStyleSheet("background-color: darkgray; border-radius: 8px")

        self.btn1.setStyleSheet("background-color: #336666; border-style: none; border-radius: 8px")
        self.btn2.setStyleSheet("background-color: #336666; border-style: none; border-radius: 8px")

        self.btn1.clicked.connect(self.button1Clicked)
        self.btn2.clicked.connect(self.button2Clicked)
        self.info_button.clicked.connect(self.info_buttonClicked)

        self.t = QFrame(self)
        self.t.setStyleSheet("background-color: #3c4047; back")
        self.t.setGeometry(1, 1, 998, 34)

        self.close_button = QPushButton(self)
        self.close_button.setGeometry(966, 4, 28, 28)
        self.close_button.setIcon(QIcon('closebtn.jpg'))
        self.close_button.clicked.connect(self.close_buttonClicked)
        self.close_button.setStyleSheet("border-style: none; border-radius: 8px")
        self.close_button.setIconSize(QSize(32, 32))

        self.minimize_button = QPushButton(self)
        self.minimize_button.setGeometry(930, 1, 26, 28)
        self.minimize_button.setIcon(QIcon('minm.png'))
        self.minimize_button.setIconSize(QSize(32, 32))
        self.minimize_button.clicked.connect(self.abc)

        self.visualize_button = QPushButton("Visualize", self)
        self.visualize_button.setFont(QFont("Times", 12, 65, True))
        self.visualize_button.setGeometry(18, 560, 164, 100)
        self.visualize_button.setStyleSheet("background-color: #FFC0CB; border-style: none; border-radius: 8px")
        self.visualize_button.clicked.connect(self.visualize_clicked)

        self.get_file_button = QPushButton("Result", self)
        self.get_file_button.setGeometry(400, 46, 125, 83)
        self.get_file_button.setStyleSheet("background-color: #336666; border-style: none; border-radius: 8px")
        self.get_file_button.setFont(QFont("Times", 12, 65, True))
        self.get_file_button.clicked.connect(self.get_file_clicked)

        self.random_generated = QPushButton("Generate\nrandom", self)
        self.random_generated.setGeometry(550, 46, 125, 83)
        self.random_generated.setStyleSheet("background-color: #336666; border-style: none; border-radius: 8px")
        self.random_generated.setFont(QFont("Times", 12, 65, True))
        self.random_generated.clicked.connect(self.random_generation)

        self.black_bckgr = QFrame(self)
        self.black_bckgr.setStyleSheet("background-color: #3c4047; back")
        self.black_bckgr.move(200, 155)
        self.black_bckgr.resize(778, 510)

        self.pixmap = QPixmap("imageee.jpg")
        self.lbl = QLabel(self)
        self.lbl.setPixmap(self.pixmap)
        self.lbl.move(205, 160)
        self.lbl.resize(770, 500)
        self.lbl.hide()

        self.chose_alg = QComboBox(self)
        self.chose_alg.addItems(["-", "DFS", "Dijkstra's algorithm", "Find bridges", "Check, is graph a tree"])

        self.chose_alg.setGeometry(18, 155, 164, 30)

        self.chose_alg.activated[str].connect(self.onActivated)

        self.edit_button = QPushButton('Edit', self)
        self.edit_button.setGeometry(250, 46, 125, 83)
        self.edit_button.setStyleSheet("background-color: #336666; border-style: none; border-radius: 8px")
        self.edit_button.setFont(QFont("Times", 12, 65, True))

    def abc(self):
        self.showMinimized()

    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.new_graph = Graph()

        self.showButtons()
        self.setStyleSheet('QMainWindow{background-color: darkgray;border: 1px solid black;}')
        self.setWindowTitle('Graph application')

        self.show()

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Exit',
                                     "Are you sure to quit?", QMessageBox.Yes |
                                     QMessageBox.No, QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
        self.close()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def button1Clicked(self):
        global maingraph
        dialog = AddGraphApplication()
        self.dialogs.append(dialog)
        dialog.show()

    def button2Clicked(self):
        global maingraph
        root = tk.Tk()
        root.withdraw()

        file_path = filedialog.askopenfilename()
        input_file = open(file_path, 'r').read().split('\n')
        n, m = map(int, input_file[0].split(' '))
        self.new_graph.set_vertices(n)
        self.new_graph.set_edges(m)
        self.new_graph.create()
        print(input_file[1:])
        for edge in input_file[1:]:
            if edge != '':
                pair = list(map(int, edge.split(' ')))
                print(pair)
                self.new_graph.add_edge(pair[0], pair[1])

        maingraph = self.new_graph

    def info_buttonClicked(self):
        dialog = InfoApplication()
        self.dialogs.append(dialog)
        dialog.show()

    def close_buttonClicked(self):
        self.close()

    def get_file_clicked(self):
        pass

    def visualize_clicked(self):
        self.xx()

    def show_gr(self):
        temp = QPixmap("imageee.jpg")
        self.pixmap = temp
        self.lbl.clear()
        self.lbl.setPixmap(self.pixmap)
        self.lbl.show()

    def onActivated(self, text):
        pass

    def random_generation(self):
        test_graph = []
        rnd.seed(time.time())
        m = rnd.randint(15, 55)
        for i in range(m):
            x, y = rnd.randint(1, 20), rnd.randint(1, 20)
            test_graph.append([x, y])

        self.new_graph.add_edge_list_unweighted(test_graph)
        self.visualize_by_new_graph()

    def visualize_by_new_graph(self):
        visualization = GraphVisualization()
        visualization.set_graph(self.new_graph.get_edge_list())
        visualization.visualize()
        self.show_gr()

    def xx(self):
        self.new_graph = maingraph
        self.visualize_by_new_graph()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainApplication()
    sys.exit(app.exec_())
