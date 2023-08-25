# -*- coding: utf-8 -*-
from PySide2 import QtCore, QtWidgets

from ..panels import ABTab
from ...ui.style import header
from ...ui.icons import qicons
from ...ui.tables import (
    DatabasesTable,
    ProjectListWidget,
    ActivitiesBiosphereTable,
    ActivitiesBiosphereTree
)
from ...signals import signals

class ProjectTab(QtWidgets.QWidget):
    def __init__(self, parent):
        super(ProjectTab, self).__init__(parent)
        # main widgets
        self.projects_widget = ProjectsWidget()
        self.databases_widget = DatabaseWidget(self)
        self.activity_biosphere_tabs = ActivityBiosphereTabs(self)

        # Layout
        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        self.splitter.addWidget(self.databases_widget)
        self.splitter.addWidget(self.activity_biosphere_tabs)

        self.overall_layout = QtWidgets.QVBoxLayout()
        self.overall_layout.setAlignment(QtCore.Qt.AlignTop)
        self.overall_layout.addWidget(self.projects_widget)
        self.overall_layout.addWidget(self.splitter)
        self.overall_layout.addStretch()
        self.setLayout(self.overall_layout)

        self.connect_signals()

    def connect_signals(self):
        signals.project_selected.connect(self.change_project)
        signals.database_selected.connect(self.update_widgets)
        signals.database_changed.connect(self.update_widgets)

    def change_project(self):
        self.update_widgets()

    def update_widgets(self):
        """Update widgets when a new database has been selected or the project has been changed.
        Hide empty widgets (e.g. Biosphere Flows table when an inventory database is selected)."""
        no_databases = len(self.activity_biosphere_tabs.tabs) == 0

        self.databases_widget.update_widget()

        self.activity_biosphere_tabs.setVisible(not no_databases)
        self.resize_splitter()

    def resize_splitter(self):
        """Splitter sizes need to be reset (for some reason this is buggy if not done like this)"""
        widgets = [self.databases_widget, self.activity_biosphere_tabs]
        sizes = [x.sizeHint().height() for x in widgets]
        tabheight = self.height()
        if sum(sizes) > tabheight and sizes[1] > 0.75 * tabheight:
            sizes[0] = sizes[1] // 3
        self.splitter.setSizes(sizes)


class ProjectsWidget(QtWidgets.QWidget):
    def __init__(self):
        super(ProjectsWidget, self).__init__()
        self.projects_list = ProjectListWidget()

        # Buttons
        self.new_project_button = QtWidgets.QPushButton(qicons.add, "New")
        self.new_project_button.setToolTip('Make a new project')
        self.copy_project_button = QtWidgets.QPushButton(qicons.copy, "Copy")
        self.copy_project_button.setToolTip('Copy the project')
        self.delete_project_button = QtWidgets.QPushButton(
            qicons.delete, "Delete"
        )
        self.delete_project_button.setToolTip('Delete the project')

        self.construct_layout()
        self.connect_signals()

    def connect_signals(self):
        self.new_project_button.clicked.connect(signals.new_project.emit)
        self.delete_project_button.clicked.connect(signals.delete_project.emit)
        self.copy_project_button.clicked.connect(signals.copy_project.emit)

    def construct_layout(self):
        h_widget = QtWidgets.QWidget()
        h_layout = QtWidgets.QHBoxLayout()
        h_layout.setAlignment(QtCore.Qt.AlignLeft)
        h_layout.addWidget(header('Project:'))
        h_layout.addWidget(self.projects_list)
        h_layout.addWidget(self.new_project_button)
        h_layout.addWidget(self.copy_project_button)
        h_layout.addWidget(self.delete_project_button)
        h_widget.setLayout(h_layout)

        # Overall Layout
        layout = QtWidgets.QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignTop)
        layout.addWidget(h_widget)
        self.setLayout(layout)

        self.setSizePolicy(QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Maximum,
            QtWidgets.QSizePolicy.Maximum)
        )


class DatabaseWidget(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.table = DatabasesTable()
        self.table.setToolTip("To select a database, double-click on an entry")

        # Temporary inclusion to explain things before checkbox is back
        self.label_change_readonly = QtWidgets.QLabel(
            "To change a database from read-only to editable and back," +
            " click on the checkbox in the table."
        )

        # Buttons
        self.add_default_data_button = QtWidgets.QPushButton(
            qicons.import_db, "Add default data (biosphere flows and impact categories)"
        )
        self.new_database_button = QtWidgets.QPushButton(qicons.add, "New")
        self.new_database_button.setToolTip('Make a new database')
        self.import_database_button = QtWidgets.QPushButton(qicons.import_db, "Import")
        self.import_database_button.setToolTip('Import a new database')

        self._construct_layout()
        self._connect_signals()

    def _connect_signals(self):
        self.add_default_data_button.clicked.connect(signals.install_default_data.emit)
        self.import_database_button.clicked.connect(signals.import_database.emit)
        self.new_database_button.clicked.connect(signals.add_database.emit)

    def _construct_layout(self):
        header_widget = QtWidgets.QWidget()
        header_layout = QtWidgets.QHBoxLayout()
        header_layout.setAlignment(QtCore.Qt.AlignLeft)
        header_layout.addWidget(header("Databases:"))
        header_layout.addWidget(self.add_default_data_button)
        header_layout.addWidget(self.new_database_button)
        header_layout.addWidget(self.import_database_button)
        header_widget.setLayout(header_layout)

        # Overall Layout
        layout = QtWidgets.QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignTop)
        layout.addWidget(header_widget)
        layout.addWidget(self.label_change_readonly)
        layout.addWidget(self.table)
        self.setLayout(layout)

    def update_widget(self):
        no_databases = self.table.rowCount() == 0
        self.add_default_data_button.setVisible(no_databases)
        self.import_database_button.setVisible(not no_databases)
        self.new_database_button.setVisible(not no_databases)

        self.table.setVisible(not no_databases)
        self.label_change_readonly.setVisible(not no_databases)


class ActivityBiosphereTabs(ABTab):
    def __init__(self, parent=None):
        super(ActivityBiosphereTabs, self).__init__(parent)
        self.setTabsClosable(True)

        self.connect_signals()

    def connect_signals(self) -> None:
        self.tabCloseRequested.connect(self.close_tab)
        signals.database_selected.connect(self.open_or_focus_tab)
        signals.database_changed.connect(self.update_activity_biosphere_widget)
        signals.delete_database_confirmed.connect(self.close_tab_by_tab_name)

        signals.project_selected.connect(self.close_all)

    def open_or_focus_tab(self, db_name: str) -> None:
        """Put focus on tab, if not open yet, open it.
        """
        # create the tab if it doesn't exist yet
        if not self.tabs.get(db_name, False):
            widget = ActivityBiosphereWidget(parent=self, database_name=db_name)
            self.add_tab(widget, db_name)
            self.update_activity_biosphere_widget(db_name)

        # put the focus on this tab + send signal that this is the open db
        self.select_tab(self.tabs[db_name])

    def current_index_changed(self, current_index: int) -> None:
        db_name = self.get_tab_name_from_index(current_index)
        signals.database_tab_open.emit(db_name)

    def update_activity_biosphere_widget(self, db_name: str) -> None:
        """Check if database is open, if so, update the underlying data"""
        if self.tabs.get(db_name, False):
            self.tabs[db_name].sync_data(db_name)


class ActivityBiosphereWidget(QtWidgets.QWidget):
    def __init__(self, parent, database_name):
        super(ActivityBiosphereWidget, self).__init__(parent)
        self.database_name = database_name

        self.table = ActivitiesBiosphereTable(self)
        self.tree = None

        # Header widget
        self.header_widget = QtWidgets.QWidget()
        self.header_layout = QtWidgets.QHBoxLayout()
        self.header_layout.setAlignment(QtCore.Qt.AlignLeft)
        self.header_widget.setLayout(self.header_layout)

        self.setup_search()

        self.mode_radio_list = QtWidgets.QRadioButton("List view")
        self.mode_radio_list.setChecked(True)
        self.mode_radio_list.setToolTip("List view of the database")
        self.mode_radio_list.hide()
        self.mode_radio_tree = QtWidgets.QRadioButton("Tree view")
        self.mode_radio_tree.setToolTip("Tree view of the database")
        self.mode_radio_tree.hide()

        self.header_layout.addWidget(self.mode_radio_list)
        self.header_layout.addWidget(self.mode_radio_tree)

        # Overall Layout
        self.v_layout = QtWidgets.QVBoxLayout()
        self.v_layout.setAlignment(QtCore.Qt.AlignTop)
        self.v_layout.addWidget(self.header_widget)
        self.v_layout.addWidget(self.table)
        self.setLayout(self.v_layout)

        self.table.setSizePolicy(QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred,
            QtWidgets.QSizePolicy.Maximum)
        )

        self.connect_signals()

    def create_tree(self):
        print('++ Starting tree creation')
        self.tree = QtWidgets.QLabel('This is a placeholder for the tree')
        self.tree = ActivitiesBiosphereTree(self, self.database_name)
        self.v_layout.addWidget(self.tree)

    def connect_signals(self):
        self.mode_radio_tree.toggled.connect(self.update_view)

    def reset_widget(self):
        self.hide()
        self.table.model.clear()

    def setup_search(self):
        # 1st search box
        self.search_box = QtWidgets.QLineEdit()
        self.search_box.setPlaceholderText("Search")
        self.search_box.returnPressed.connect(self.set_search_term)

        # search
        self.search_button = QtWidgets.QToolButton()
        self.search_button.setIcon(qicons.search)
        self.search_button.setToolTip("Filter activities")
        self.search_button.clicked.connect(self.set_search_term)

        # reset search
        self.reset_search_button = QtWidgets.QToolButton()
        self.reset_search_button.setIcon(qicons.delete)
        self.reset_search_button.setToolTip("Clear the search")
        self.reset_search_button.clicked.connect(self.table.reset_search)
        self.reset_search_button.clicked.connect(self.search_box.clear)

        signals.project_selected.connect(self.search_box.clear)
        self.header_layout.addWidget(self.search_box)

        self.header_layout.addWidget(self.search_button)
        self.header_layout.addWidget(self.reset_search_button)

    def set_search_term(self):
        search_term = self.search_box.text()
        self.table.search(search_term)

    @QtCore.Slot(bool, name="isListToggled")
    def update_view(self, toggled: bool):
        self.table.setVisible(not toggled)

        #if not isinstance(self.tree, QtWidgets.QLabel):
        if not isinstance(self.tree, ActivitiesBiosphereTree):
            self.create_tree()
        self.tree.setVisible(toggled)

    def sync_data(self, db_name: str) -> None:
        self.table.model.sync(db_name)

        # if 'ISIC rev.4 ecoinvent' in self.table.model._dataframe.columns \
        #         and not isinstance(self.tree, QtWidgets.QLabel):
        if 'ISIC rev.4 ecoinvent' in self.table.model._dataframe.columns and not isinstance(self.tree, ActivitiesBiosphereTree):
            # a treeview does not exist and should be able to navigate to

            # set the view to list and show the radio buttons
            self.mode_radio_list.setChecked(True)
            self.mode_radio_tree.setChecked(False)
            self.mode_radio_list.show()
            self.mode_radio_tree.show()
        elif 'ISIC rev.4 ecoinvent' in self.table.model._dataframe.columns:
            # a treeview exists

            # make sure that the radio buttons are available
            self.mode_radio_list.show()
            self.mode_radio_tree.show()
        else:
            # a treeview does not need to be shown

            # delete the tree if it exists
            if isinstance(self.tree, ActivitiesBiosphereTree):
                self.tree.hide()
                self.tree = None
            # set the view to list and hide radio buttons
            self.mode_radio_list.hide()
            self.mode_radio_tree.hide()
            self.table.show()
