import json
from ast import literal_eval
from subprocess import Popen


from PyQt5.QtWidgets import (QAbstractItemView, QApplication, QButtonGroup,
                             QHBoxLayout, QHeaderView, QLabel, QLineEdit,
                             QMainWindow, QPushButton, QRadioButton,
                             QTableWidget, QTableWidgetItem, QVBoxLayout,
                             QWidget)

HEADERS = ["Name", "Edition", "Authors", "Topics", "Publisher"]
with open("library.json", "r") as f: # use if running script directly
# with open("Pybrary/library.json", "r") as f: # use if runnning from batch file

    BOOK_DICT = json.load(f)
    for book in BOOK_DICT:
        # convert author entries into nice strings
        book["authors"] = ", ".join(map(str, book["authors"]))
        book["topics"] = ", ".join(map(str, book["topics"]))
    BOOK_DICT.sort(key=lambda book: book["edition"])
    BOOK_DICT.sort(key=lambda book: book["name"])


def query_book_dict(query="", field="") -> dict:
    '''takes a query and a field. Returns all books that have <query> in <field>
    If query is an empty string, return all books'''
    rep = []

    if not query:
        rep = BOOK_DICT
        return rep

    for book in BOOK_DICT:
        if query.lower() in str(book[field]).lower():
            rep.append(book)

    return rep


class ResultsTable(QTableWidget):
    '''generates results table widget.'''

    def __init__(self):
        super().__init__()
        # prevents cell editing
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.setSortingEnabled(True)
        self.setRowCount(len(BOOK_DICT))
        self.setColumnCount(len(HEADERS))
        self.setHorizontalHeaderLabels(HEADERS)

        for i in range(0, 2):
            # have name and edition columns take up the space they need
            self.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeToContents)
        for i in range(2, 5):
            # set other columns to fill up rest of available space
            self.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)

        self.update_table(query_book_dict())

    def open_pdf(self):
        '''opens pdf associated with current line selected'''

        row = int(self.currentRow())
        dat = {}

        for colnum, col in enumerate(HEADERS):
            dat[col.lower()] = self.item(row, colnum).text()

        dat["edition"] = int(dat["edition"])
        if type(dat["authors"]) == list:
            # convert from list to str
            dat["authors"] = literal_eval(dat["authors"])

        for book in BOOK_DICT:
            if dat.items() <= book.items():  # checks if book contains dat
                Popen([book["location"]], shell=True)
                return

    def update_table(self, books: dict):
        '''takes a dict and refreshes table with entries'''

        self.setRowCount(len(books))
        self.setColumnCount(len(HEADERS))
        self.setHorizontalHeaderLabels(HEADERS)
        for row, book in enumerate(books):
            for col, header in enumerate(HEADERS):
                self.setItem(
                    row,
                    col,
                    QTableWidgetItem(str(book[header.lower()])))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self._createToolBars()
        self.setWindowTitle("Pybary")
        self.setGeometry(0, 0, 750, 500)

        # add vertically stacked box layout
        self.page_layout = QVBoxLayout()

        # add input bar to layout
        self.input_bar = QLineEdit()
        self.input_bar.returnPressed.connect(self.make_search)
        self.page_layout.addWidget(self.input_bar)

        # add radio buttons -----

        # group to hold buttons so only one can be selected
        self.searchby_button_group = QButtonGroup()
        self.searchby_button_layout = QHBoxLayout()  # lay buttons out horizontally
        self.searchby_radio_buttons = []  # list to hold the butotns

        self.searchby_button_layout.addWidget(QLabel("Search by: "))

        for header in HEADERS:
            new_button = QRadioButton(header)
            self.searchby_radio_buttons.append(new_button)
            self.searchby_button_group.addButton(new_button)
            self.searchby_button_layout.addWidget(new_button)

        # create table of results -----
        # this is done early so that the results table can be referenced
        self.results_table = ResultsTable()

        # add button to make search -----
        self.make_search_button = QPushButton("Search")
        self.make_search_button.clicked.connect(self.make_search)
        self.searchby_button_layout.addWidget(self.make_search_button)

        # add button to clear search -----
        self.clear_serach_button = QPushButton("Clear")
        self.clear_serach_button.clicked.connect(
            lambda: self.results_table.update_table(query_book_dict()))
        self.searchby_button_layout.addWidget(self.clear_serach_button)

        # adds radio buttons and search butotn to GUI
        self.page_layout.addLayout(self.searchby_button_layout)

        # add table of results to layout -----
        self.page_layout.addWidget(self.results_table)

        # add open pdf button -----
        self.open_pdf_button = QPushButton("Open pdf")
        self.open_pdf_button.clicked.connect(self.results_table.open_pdf)
        self.page_layout.addWidget(self.open_pdf_button)

        # final setup -----
        self.widget = QWidget()
        self.widget.setLayout(self.page_layout)
        self.setCentralWidget(self.widget)

    def _createToolBars(self):
        mainToolBar = self.addToolBar("Main")

    def make_search(self):
        query = self.input_bar.text()
        try:
            field = self.searchby_button_group.checkedButton().text().lower()
        except AttributeError:
            # no field selected
            field = "name"

        self.results_table.update_table(query_book_dict(query, field))


app = QApplication([])
window = MainWindow()
window.show()
app.exec()
