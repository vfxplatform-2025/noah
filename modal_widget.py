# -*- coding: utf-8 -*-
__author__ = 'hyunil'
import os
import json
import glob
import xmltodict
from operator import itemgetter
import re
import stat
import time
from pprint import pprint
from cacheExport_module.pyside2_moduleImport import *
from cacheExport_module.assetsExport_moduleImport import *
import imp
# from PySide2 import QtWidgets, QtGui, QtCore
imp.reload(takeScript)

HORIZONTAL_HEADERS = ("", "AUTHOR", "NAME", "VERSION", "SUBJECT", "DATE", "FILE", "COMMENT", "COUNT", "NAME_SPACE", "SET")


class SortFilterProxyModel(QtCore.QSortFilterProxyModel):

    def __init__(self, *args, **kwargs):
        QtCore.QSortFilterProxyModel.__init__(self, *args, **kwargs)
        self.filters = {}
        self.setRecursiveFilteringEnabled = True

    def setFilterRegExp(self, pattern):
        if isinstance(pattern, str):
            pattern = QtCore.QRegExp(
                pattern, QtCore.Qt.CaseInsensitive,
                QtCore.QRegExp.FixedString)

        super(SortFilterProxyModel, self).setFilterRegExp(pattern)

    def setFilterByColumn(self, regex, column):
        self.filters[column] = regex
        self.invalidateFilter()

    def clear_filter(self):
        self.filters = {}
        self.invalidateFilter()

    def _accept_index(self, idx):
        if idx.isValid():
            text = idx.data(QtCore.Qt.DisplayRole)

            if self.filterRegExp().indexIn(str(text)) >= 0:
                return True

            for row in range(idx.model().rowCount(idx)):
                if self._accept_index(idx.model().index(row, 0, parent=idx)):
                    return True

        return False

    def filterAcceptsRow(self, sourceRow, sourceParent):
        idx = self.sourceModel().index(sourceRow, 0, sourceParent)
        return self._accept_index(idx)


class SelectSet(QtWidgets.QDialog):

    THUMBNAIL, AUTHOR, NAME, SUBJECT, DATE, FILE, COMMMENT, COUNT = list(range(8))

    def __init__(self, assets=None, currentobjs=None,  parent=None):
        super(SelectSet, self).__init__(parent)
        self.assets = assets
        self.currentobjs = currentobjs
        self.IMPORT_TYPE = ['reference', 'import']
        self.WORKCODE_TYPE = ['All', 'clothSim', 'dyn', 'hairSim', 'muscleSim', 'rig']
        self.asset_pub_files = []
        self.all_asset_files = []

        self.setupUI()
        self.import_type = ''
        self.set_type = ''
        self.workcode_type = ''

    def setupUI(self):
        self.setGeometry(1100, 200, 1024, 600)
        self.setWindowTitle("select SET")
        self.model = None

        layout = QtWidgets.QVBoxLayout()

        import_type_layout = QtWidgets.QHBoxLayout()

        self.import_type_lb = QtWidgets.QLabel()
        self.import_type_lb.setText("Import type: ")
        self.import_type_cmb = QtWidgets.QComboBox()

        self.import_type_cmb.addItems(self.IMPORT_TYPE)
        import_type_layout.addWidget(self.import_type_lb)
        import_type_layout.addWidget(self.import_type_cmb)

        workcode_type_layout = QtWidgets.QHBoxLayout()
        self.workcode_type_lb = QtWidgets.QLabel()
        self.workcode_type_lb.setText("Workcode : ")
        self.workcode_type_cmb = QtWidgets.QComboBox()
        self.workcode_type_cmb.addItems(self.WORKCODE_TYPE)
        workcode_type_layout.addWidget(self.workcode_type_lb)
        workcode_type_layout.addWidget(self.workcode_type_cmb)

        fn_button_layout = QtWidgets.QHBoxLayout()
        spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.uncheck_all_btn = QtWidgets.QPushButton("uncheck all")
        self.uncheck_all_btn.setMaximumSize(100,100)
        self.auto_check_all_btn = QtWidgets.QPushButton("auto check all")
        self.auto_check_all_btn.setMaximumSize(100,100)
        fn_button_layout.addItem(spacer)
        fn_button_layout.addWidget(self.uncheck_all_btn)
        fn_button_layout.addWidget(self.auto_check_all_btn)

        self.get_pub_datas(self.workcode_type_cmb.currentText())
        self.asset_treeview = QtWidgets.QTreeView()

        self.proxy_model_workcode = SortFilterProxyModel()
        self.proxy_model_workcode.setDynamicSortFilter(True)
        self.asset_treeview.setItemsExpandable(True)

        self.update_model()

        self.summit_btn = QtWidgets.QPushButton()
        self.summit_btn.setText('Import atom')

        layout.addLayout(import_type_layout)
        layout.addLayout(workcode_type_layout)
        layout.addLayout(fn_button_layout)
        layout.addWidget(self.asset_treeview)
        layout.addWidget(self.summit_btn)
        self.setLayout(layout)

        self.workcode_type_cmb.currentIndexChanged.connect(self.filter_treeview)
        self.uncheck_all_btn.clicked.connect(self.uncheck_all)
        self.auto_check_all_btn.clicked.connect(self.auto_check)
        self.summit_btn.clicked.connect(self.import_summit)

    def update_model(self):
        self.model = AssetTreeModel(self.asset_pub_files)
        self.proxy_model_workcode.setSourceModel(self.model)
        self.proxy_model_workcode.setFilterCaseSensitivity(QtCore.Qt.CaseSensitive)

        self.asset_treeview.setModel(self.proxy_model_workcode)
        self.asset_treeview.expandAll()
        self.asset_treeview.setSortingEnabled(True)
        self.asset_treeview.header().setStretchLastSection(True)
        for i in range(self.asset_treeview.header().count()):
            self.asset_treeview.resizeColumnToContents(i)

    @staticmethod
    def get_wip(file_path):
        return re.search('(?<=_w)\d{2,3}', file_path).group() if re.search('(?<=_w)\d{2,3}', file_path) else ''

    @staticmethod
    def get_ver(file_path):
        return re.search('(?<=_v)\d{2,3}', file_path).group() if re.search('(?<=_v)\d{2,3}', file_path) else ''

    def get_subject(self, filepath):
        wip = self.get_wip(filepath)
        if wip:
            divided = filepath.rpartition(wip)
        else:
            ver = self.get_ver(filepath)
            if not ver:
                return
            divided = filepath.rpartition(ver)
        reg = re.search("(?<=_).+?(?=\.mb)", divided[-1])
        return reg.group() if reg else ''

    def get_xml_data(self, xmlfile, asset_dir, asset_workcode, current_asset_version):
        pub_assets = []

        def get_data(data):
            xml_data = dict()
            mayafile = "{0}/{1}".format(asset_dir, data['@filename'])
            mdate = os.stat(mayafile)[stat.ST_MTIME] if os.path.isfile(mayafile) else ''
            xml_data['file'] = mayafile
            xml_data['subject'] = self.get_subject(mayafile)
            xml_data['comment'] = data['comment']
            xml_data['author'] = data['author']
            xml_data['date'] = time.strftime('%Y-%m-%d %H:%M', time.localtime(mdate)) if mdate else ''
            xml_data['version'] = self.get_ver(mayafile)
            xml_data['thumbnail'] = "{0}/{1}.jpg".format(os.path.dirname(xmlfile),
                                                         os.path.splitext(data['@filename'])[0])
            # xml_data['res'] = None
            xml_data['asset_workcode'] = asset_workcode
            pub_assets.append(xml_data)

        def get_pub_data(mayafile):
            pub_data = dict()
            mdate = os.stat(mayafile)[stat.ST_MTIME] if os.path.isfile(mayafile) else ''
            pub_data['file'] = mayafile
            pub_data['subject'] = self.get_subject(mayafile)
            pub_data['comment'] = ''
            pub_data['author'] = ''
            pub_data['date'] = time.strftime('%Y-%m-%d %H:%M', time.localtime(mdate)) if mdate else ''
            pub_data['version'] = self.get_ver(mayafile)
            pub_data['thumbnail'] = ''

            pub_data['asset_workcode'] = asset_workcode
            pub_assets.append(pub_data)

        with open(xmlfile, 'r') as f:
            xmlString = f.read()
        try:
            jsonString = json.dumps(xmltodict.parse(xmlString), indent=4)
            asset_data = json.loads(jsonString)['root']['file']

            if isinstance(asset_data, dict):
                get_data(asset_data)
            elif isinstance(asset_data, list):
                for data in asset_data:
                    get_data(data)
        except:
            asset_data = glob.glob("{}/*.mb".format(asset_dir))
            # version = 0
            latest_versions = list()
            for mayafile in sorted(asset_data):
                if self.get_ver(mayafile) >= current_asset_version:
                    print(mayafile)
                    get_pub_data(mayafile)

        return pub_assets

    def get_pub_datas(self, filter_workcode):
        for asset in self.assets:
            current_asset_version = self.get_ver(asset['current_rig_path'])

            pub_files = dict()
            assets_dir_list = list()
            pub_data = list()

            asset_name = asset['name'].split(':')[-1]
            asset_namespace = [asset['name'].split(':')[0] for asset in self.assets if
                               asset['name'].split(':')[-1] == asset_name]
            count = 0

            if asset_name not in [_asset['name'] for _asset in self.asset_pub_files]:
                for asset_workcode in self.WORKCODE_TYPE:
                    asset_dir = "{0}assets/cha/{1}/{2}/pub".format(os.path.dirname(asset['atom_path']).split('seq')[0],
                                                                   asset_name,
                                                                   asset_workcode)
                    asset_xml_file = '{}/.lib/{}_{}.xml'.format(asset_dir,
                                                                asset_name,
                                                                asset_workcode)

                    if os.path.exists(asset_dir) and os.path.exists(asset_xml_file):
                        assets_dir_list.append(asset_dir)
                        for pub_file in self.get_xml_data(asset_xml_file, asset_dir, asset_workcode, current_asset_version):
                            pub_data.append(pub_file)

                pub_files['name'] = asset_name
                pub_files['asset_dirs'] = assets_dir_list
                pub_files['pub_data'] = pub_data
                count += 1
                pub_files['count'] = count
                pub_files['name_space'] = asset_namespace
                atom_set_type = 'ctrl_SET'
                if "_SET" in asset['atom_path']:
                    atom_set_type = "{}_SET".format(os.path.basename(asset['atom_path']).split('_')[1])
                pub_files['set_type'] = atom_set_type

                self.asset_pub_files.append(pub_files)

            else:
                for _asset in self.asset_pub_files:
                    if _asset['name'] == asset_name:
                        _asset['count'] = _asset['count'] + 1
        return

    @QtCore.Slot(int)
    def filter_treeview(self, workcode):
        self.proxy_model_workcode.clear_filter()

        search_word = self.workcode_type_cmb.currentText()
        if self.workcode_type_cmb.currentText() == 'All':
            search_word = ''

        self.proxy_model_workcode.setFilterRegExp(search_word)
        self.asset_treeview.expandAll()

        latest_versions = []

        for items in self.model.rootItem.childItems:
            ver = 0
            version_item = None
            for item in items.childItems:
                if search_word != '':
                    self.uncheck_all()
                    if item.asset.version > ver and search_word in item.asset.name:
                        ver = item.asset.version
                        version_item = item

            latest_versions.append(version_item)
        if search_word != '':
            for item in latest_versions:
                if item:
                    item.setChecked(True)

    @QtCore.Slot()
    def uncheck_all(self):
        for items in self.model.rootItem.childItems:
            for item in items.childItems:
                item.setChecked(False)
        self.asset_treeview.expandAll()

    @QtCore.Slot()
    def auto_check(self):
        self.uncheck_all()
        for items in self.model.rootItem.childItems:
            version = 0
            latest_item = None
            for item in items.childItems:
                name = item.asset.name.split('_')[-1]
                set_type = item.asset.set_type
                type_check = False

                if name in ['dyn'] and set_type == "mocapJointBake_SET":
                    type_check = True
                elif name in ['crowdSim', 'hairSim', 'muscleSim', 'rig'] and set_type == "ctrl_SET":
                    type_check = True

                if type_check:
                    if version < item.asset.version:
                        if latest_item:
                            latest_item.setChecked(False)
                        version = item.asset.version
                        latest_item = item
                        item.setChecked(True)

    def import_summit(self):
        self.import_type = self.import_type_cmb.currentText()
        self.set_type = '1'
        self.workcode_type = self.workcode_type_cmb.currentText()
        self.all_asset_files = []

        for items in self.model.rootItem.childItems:
            for item in items.childItems:
                if item.checked():
                    for namespace in item.asset.namespace:
                        asset_item = dict()
                        name = "{}:{}".format(namespace, item.asset.asset_name)
                        asset_item['name'] = name
                        asset_item['file'] = item.asset.file

                        self.all_asset_files.append(asset_item)
        pprint(self.all_asset_files)
        self.close()

    def closeEvent(self, event):
        if self.set_type:
            event.accept()


class AssetDataClass(object):

    def __init__(self, name, thumbnail, author, subject, date, file, comment, count, asset_workcode, version, namespace, settype):
        self.name = "{}_{}".format(name, asset_workcode)
        self.asset_name = name
        self.thumb_nail = thumbnail
        self.author = author
        self.subject = subject
        self.date = date
        self.file = file
        self.comment = comment
        self.count = count
        self.version = version
        self.namespace = namespace
        self.set_type = settype


class TreeItem(object):
    '''
    a python object used to return row/column data, and keep note of
    it's parents and/or children
    '''

    def __init__(self, asset, header, parentItem, checked=False):
        self.asset = asset
        self.parentItem = parentItem
        self.header = header
        self.childItems = []
        self.setChecked(checked)

    def appendChild(self, item):
        self.childItems.append(item)

    def child(self, row):
        return self.childItems[row]

    def childCount(self):
        return len(self.childItems)

    def columnCount(self):
        return len(HORIZONTAL_HEADERS)

    def data(self, column):
        if self.asset == None:
            if column == 0:
                return self.header
            else:
                None
        else:
            if column == 0:
                return self.asset.name
            if column == 1:
                return self.asset.author
            if column == 2:
                return self.asset.name
            if column == 3:
                return self.asset.version
            if column == 4:
                return self.asset.subject
            if column == 5:
                return self.asset.date
            if column == 6:
                return self.asset.file
            if column == 7:
                return self.asset.comment
            if column == 8:
                return self.asset.count
            if column == 9:
                return str(self.asset.namespace)
            if column == 10:
                return str(self.asset.set_type)
        return None

    def parent(self):
        return self.parentItem

    def row(self):
        if self.parentItem:
            return self.parentItem.childItems.index(self)
        return 0

    def checked(self):
        return self._checked

    def setChecked(self, checked=True):
        self._checked = bool(checked)


class AssetTreeModel(QtCore.QAbstractItemModel):

    def __init__(self, data=None, parent=None):
        super(AssetTreeModel, self).__init__(parent)
        self.asset_data = []

        for asset in data:
            for pub in sorted(asset['pub_data'], key=itemgetter('date'), reverse=True):
                asset_list = [_asset.file for _asset in self.asset_data]
                assets = AssetDataClass(
                    asset['name'], pub['thumbnail'], pub['author'], pub['subject'], pub['date'], pub['file'],
                    pub['comment'], asset['count'], pub['asset_workcode'], pub['version'], asset['name_space'],
                    asset['set_type']
                )
                if assets.file not in asset_list:
                    self.asset_data.append(assets)

        self.rootItem = TreeItem(None, "ALL", None)
        self.parents = {0: self.rootItem}
        self.setupModelData()

    def columnCount(self, parent=None):
        if parent and parent.isValid():
            return parent.internalPointer().columnCount()
        else:
            return len(HORIZONTAL_HEADERS)

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if index.isValid():
            if role == QtCore.Qt.CheckStateRole:
                node = index.internalPointer()
                node.setChecked(not node.checked())
                return True
        return False

    def data(self, index, role):
        if not index.isValid():
            return None

        item = index.internalPointer()
        node = self.nodeFromIndex(index)

        if role == QtCore.Qt.DisplayRole:
            return item.data(index.column())

        if role == QtCore.Qt.BackgroundRole:
            if node.asset is None:
                return None
            name = node.asset.name.split('_')[-1]
            set_type = node.asset.set_type
            if name in ['dyn']:
                if set_type == "mocapJointBake_SET":
                    return QtGui.QBrush(QtGui.QColor(26,26,26))
            elif name in ['crowdSim','hairSim', 'muscleSim']:
                if set_type == "ctrl_SET":
                    return QtGui.QBrush(QtGui.QColor(46, 46, 46))

            return QtGui.QBrush(QtGui.QColor(64, 64, 64))

        if role == QtCore.Qt.CheckStateRole:
            if index.column() == 0:
                if node.checked():
                    return QtCore.Qt.Checked
                return QtCore.Qt.Unchecked

        if role == QtCore.Qt.UserRole:
            if item:
                return item.asset

        return None

    def headerData(self, column, orientation, role):
        if (orientation == QtCore.Qt.Horizontal and
                role == QtCore.Qt.DisplayRole):
            try:
                return HORIZONTAL_HEADERS[column]
            except IndexError:
                pass

        return None

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QtCore.QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()

        childItem = index.internalPointer()
        if not childItem:
            return QtCore.QModelIndex()

        parentItem = childItem.parent()

        if parentItem == self.rootItem:
            return QtCore.QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent=QtCore.QModelIndex()):
        if parent.column() > 0:
            return 0
        if not parent.isValid():
            p_Item = self.rootItem
        else:
            p_Item = parent.internalPointer()
        return p_Item.childCount()

    def setupModelData(self):
        for asset in self.asset_data:
            asset_name = asset.asset_name
            if asset_name not in self.parents:
                newparent = TreeItem(None, asset_name, self.rootItem)
                self.rootItem.appendChild(newparent)

                self.parents[asset_name] = newparent

            parentItem = self.parents[asset_name]
            newItem = TreeItem(asset, HORIZONTAL_HEADERS, parentItem)
            parentItem.appendChild(newItem)

    def flags(self, index):
        if index.column() == 0:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsUserCheckable
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def nodeFromIndex(self, index):
        return index.internalPointer() if index.isValid() else self.root
