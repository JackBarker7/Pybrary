import json
from ast import literal_eval
from subprocess import Popen
from PyQt5.QtGui import QIcon
import qrc_resources
from copy import deepcopy, error
from os import getcwd

from PyQt5.QtWidgets import (
    QAbstractItemView,
    QAction,
    QApplication,
    QButtonGroup,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


BOOK_LIST = []
KEYS = ["Location", "Name", "Edition", "Authors", "Topics", "Publisher", "Storage_type"]
HEADERS = ["Name", "Edition", "Authors", "Topics", "Publisher"]
JSONPATH = "Pybrary/library.json"


class Book(dict):
    """a modification of dict to add a prettified version of book dicts to display in GUIs
    Book.pretty is the same dict, with the authors and topics fields formatted to remove
    square brackets etc from string representation of list"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.pretty = deepcopy(args[0])
        for field in ["authors", "topics"]:
            self.pretty[field] = ", ".join(map(str, self.pretty[field]))


with open(JSONPATH, "r") as f:

    for book in json.load(f):
        BOOK_LIST.append(Book(book))
    BOOK_LIST.sort(key=lambda book: book["edition"])
    BOOK_LIST.sort(key=lambda book: book["name"])


def show_error(text, title):
    error_box = QMessageBox()
    error_box.setIcon(QMessageBox.Critical)
    error_box.setText(text)
    error_box.setWindowTitle(title)
    error_box.exec_()


def query_book_dict(query: str = "", fields: list = []) -> dict:
    """takes a query and a field. Returns all books that have <query> in <field>
    If query is an empty string, return all books"""
    rep = []

    if not query:
        rep = BOOK_LIST
        return rep

    for book in BOOK_LIST:
        for field in fields:
            if query.lower() in str(book[field]).lower():
                rep.append(book)

    return rep


class ResultsTable(QTableWidget):
    """generates results table widget."""

    def __init__(self):
        super().__init__()
        # prevents cell editing
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.setSortingEnabled(True)
        self.setRowCount(len(BOOK_LIST))
        self.setColumnCount(len(HEADERS))
        self.setHorizontalHeaderLabels(HEADERS)

        #Allow double clicking of book to open it
        self.doubleClicked.connect(self.open_pdf)

        for i in range(0, 2):
            # have name and edition columns take up the space they need
            self.horizontalHeader().setSectionResizeMode(
                i, QHeaderView.ResizeToContents
            )
        for i in range(2, 5):
            # set other columns to fill up rest of available space
            self.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)

        self.update_table(query_book_dict())

    def get_book(self):
        """returns book associated with current line selected"""
        row = int(self.currentRow())
        dat = {}

        for colnum, col in enumerate(HEADERS):
            dat[col.lower()] = self.item(row, colnum).text()

        dat["edition"] = int(dat["edition"])
        if type(dat["authors"]) == list:
            # convert from list to str
            dat["authors"] = literal_eval(dat["authors"])

        for book in BOOK_LIST:
            if dat.items() <= book.pretty.items():  # checks if book contains dat
                return book
        return None

    def open_pdf(self):
        """opens pdf associated with current line selected"""
        try:
            file_path = self.get_book()["location"]
            Popen([file_path], shell=True)
        except AttributeError:
            show_error("No book selected!", "Error")

    def update_table(self, books: dict):
        """takes a dict and refreshes table with entries"""

        self.setRowCount(len(books))
        self.setColumnCount(len(HEADERS))
        self.setHorizontalHeaderLabels(HEADERS)
        for row, book in enumerate(books):
            for col, header in enumerate(HEADERS):
                self.setItem(
                    row, col, QTableWidgetItem(str(book.pretty[header.lower()]))
                )


class BookForm(QWidget):
    """generates a pop-up form to add a new book"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add new book")
        self.create_form()

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.form_group_box)
        self.setLayout(self.layout)

    def create_form(self):
        # form setup -----
        self.form_group_box = QGroupBox("New Book Entry")
        layout = QFormLayout()
        self.entries = {"location": QLineEdit()}

        # adding file search functionality to location row -----
        self.search_file_button = QPushButton("...")
        self.search_file_button.clicked.connect(self.open_file_dialog)
        # need a box layout as layout.addRow() only allows 2 widgets
        location_row_layout = QHBoxLayout()
        location_row_layout.addWidget(self.entries["location"])
        location_row_layout.addWidget(self.search_file_button)
        layout.addRow(QLabel("Location"), location_row_layout)

        # populate rest of table -----
        for key in KEYS[1:]:
            self.entries[key.lower()] = QLineEdit()
            layout.addRow(QLabel(key), self.entries[key.lower()])

        # add default text -----
        self.entries["storage_type"].setText("local")

        # final setup -----
        self.submit_button = QPushButton("Add book")
        self.submit_button.clicked.connect(self.add_book)
        layout.addRow(self.submit_button)
        self.form_group_box.setLayout(layout)

    def open_file_dialog(self):
        """opens a file dialog to allow user to select file to add.
        inserts relative path of file into location field of form"""
        file = QFileDialog.getOpenFileName(self, "Open file", getcwd(), "*.pdf")
        file_location = file[0].strip(getcwd().replace("\\", "/"))
        self.entries["location"].setText(file_location)

    def add_book(self):
        """gets all entries from forms, turns them into a book objects, then addds this to the master list"""
        global BOOK_LIST
        new_dict = {}
        for key in KEYS:
            key = key.lower()
            new_dict[key] = self.entries[key].text()

        new_dict["authors"] = new_dict["authors"].split(",")
        new_dict["topics"] = new_dict["topics"].split(",")

        try:
            new_dict["edition"] = int(new_dict["edition"])
        except ValueError:
            show_error("Edition must be a number!", "Error")
            self.destroy()

            return

        book = Book(new_dict)
        BOOK_LIST.append(book)
        with open(JSONPATH, "w") as f:
            json.dump(BOOK_LIST, f)
        window.results_table.update_table(query_book_dict())


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # create table of results -----
        # this is done early so that the results table can be referenced
        self.results_table = ResultsTable()

        self.createActions()
        self.createToolBars()

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

        # add button to make search -----
        self.make_search_button = QPushButton("Search")
        self.make_search_button.clicked.connect(self.make_search)
        self.searchby_button_layout.addWidget(self.make_search_button)

        # add button to clear search -----
        self.clear_serach_button = QPushButton("Clear")
        self.clear_serach_button.clicked.connect(self.clear_search)
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

    def createToolBars(self):
        mainToolBar = self.addToolBar("Main")
        mainToolBar.addAction(self.openAction)
        mainToolBar.addAction(self.saveAction)
        mainToolBar.addAction(self.deleteAction)

    def createActions(self):
        openIcon = QIcon(":open.svg")
        saveIcon = QIcon(":plus.svg")
        deleteIcon = QIcon(":minus.svg")

        self.openAction = QAction(openIcon, "Open PDF", self)
        self.saveAction = QAction(saveIcon, "Add new book", self)
        self.deleteAction = QAction(deleteIcon, "Delete book", self)

        self.openAction.triggered.connect(self.results_table.open_pdf)
        self.saveAction.triggered.connect(self.add_book)
        self.deleteAction.triggered.connect(self.delete_book)

    def make_search(self):
        """gets query and field from QLineEdit and radio buttons respectively
        uses these to update the results table"""
        query = self.input_bar.text()
        try:
            field = [self.searchby_button_group.checkedButton().text().lower()]
        except AttributeError:
            # no field selected
            field = [header.lower() for header in HEADERS]

        self.results_table.update_table(query_book_dict(query, field))

    def clear_search(self):
        self.results_table.update_table(query_book_dict())
        self.input_bar.setText("")

        #Button group has to temporarily be set to non exclusive so that all buttons can be unchecked
        self.searchby_button_group.setExclusive(False)
        for button in self.searchby_radio_buttons:
            button.setChecked(False)
        self.searchby_button_group.setExclusive(True)

    def add_book(self):
        self.new_book_gui = BookForm()
        self.new_book_gui.show()

    def delete_book(self):
        global BOOK_LIST
        confirm = QMessageBox.question(
            self,
            "Confirm delete",
            "Are you sure you want to delete?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,  # default
        )
        if confirm == QMessageBox.Yes:
            try:
                book = self.results_table.get_book()
                BOOK_LIST.remove(book)
                with open(JSONPATH, "w") as f:
                    json.dump(BOOK_LIST, f)
            except AttributeError:
                show_error("No book selected!", "Error")
        self.results_table.update_table(query_book_dict())
        return


app = QApplication([])
window = MainWindow()
window.show()
app.exec()
