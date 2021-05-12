from PySide2.QtCore import (Signal, QThread, Qt, QSettings)
from PySide2.QtGui import QCloseEvent
from PySide2.QtWidgets import (QWidget, QApplication, QDialog, QTableWidgetItem)

import time
import re
import os, sys
import platform
import subprocess

import PingMonitor_design
import PingMonitorSettings_design
import Tracert_design


class Monitor(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.ui = PingMonitor_design.Ui_Form()
        self.ui.setupUi(self)
        # settings
        self.settings = QSettings('Monitor')
        self.ips = sorted(self.load_data())
        # Thread
        self.t = IPsThread()
        self.t.started.connect(lambda: print("Поток запущен"))
        self.t.finished.connect(lambda: print("Поток завершен"))
        self.t.mysignal.connect(self.update_ip_status, Qt.QueuedConnection)
        # button clicks
        self.ui.btnSettings.clicked.connect(self.btnSettingsPressed)
        self.ui.btnTracert.clicked.connect(self.btnTracertPressed)
        self.ui.btnStart.clicked.connect(self.t.start)
        self.ui.btnStop.clicked.connect(self.stop)
        # table update
        self.update_table()
        self.ips_status = {i: None for i in self.ips}

    def load_data(self):
        if self.settings.value('ips'):
            return [i for i in self.settings.value('ips')]
        return []

    def btnSettingsPressed(self):
        setting_window = IPSettings(self, self.ips)
        setting_window.exec_()

    def btnTracertPressed(self):
        ips_to_search = []
        for index in self.ui.tblIPs.selectedItems():
            ips_to_search.append(self.ui.tblIPs.item(index.row(), 0).text())
        tracert_window = Tracert(self, ips_to_search)
        tracert_window.exec_()

    def update_table(self):
        self.ui.tblIPs.clearContents()
        for row in range(self.ui.tblIPs.rowCount()):
            self.ui.tblIPs.removeRow(row)
            print(f'row {row} removed')
        rowPosition = 0
        print(self.ips)
        for i in self.ips:
            print(f'adding {rowPosition}')
            self.ui.tblIPs.insertRow(rowPosition)
            self.ui.tblIPs.setItem(rowPosition, 0, QTableWidgetItem(i))
            rowPosition += 1

    def update_ip_status(self):
        print('run status update')
        self.ui.lblstatus.setText("Активно")
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        rowPosition = 0
        for i in self.ips:
            response = os.system(f"ping {param} 1 {i}")
            ip_status = 'on' if response != 1 else 'off'
            self.ui.tblIPs.setItem(rowPosition, 1, QTableWidgetItem(ip_status))
            if not self.ips_status[i]:
                if ip_status == 'off':
                    self.ui.txtLog.insertPlainText(f'ip {i} is unavailable on {time.ctime(time.time())}\n')
            else:
                if self.ips_status[i] != ip_status:
                    if ip_status == 'off':
                        self.ui.txtLog.insertPlainText(f'ip {i} is unavailable on {time.ctime(time.time())}\n')
                    else:
                        self.ui.txtLog.insertPlainText(f'ip {i} is available on {time.ctime(time.time())}\n')
            rowPosition += 1

    def closeEvent(self, event: QCloseEvent) -> None:
        self.settings.setValue("ips", self.ips)

    def stop(self):
        self.t.status = False
        self.ui.lblstatus.setText("Стоп")

class IPsThread(QThread):
    mysignal = Signal()
    def run(self) -> None:
        self.status = True
        while self.status:
            self.mysignal.emit()
            time.sleep(20)


class IPSettings(QDialog):
    def __init__(self, parent=None, lst_ips = []):
        super().__init__()
        self.ui = PingMonitorSettings_design.Ui_Form()
        self.ui.setupUi(self)
        self.parent = parent
        if lst_ips:
            for ip in lst_ips:
                self.ui.lstIPs.addItem(ip)
        self.ui.btnAdd.clicked.connect(self.btnAddPressed)
        self.ui.btnRemove.clicked.connect(self.btnRemovePressed)
        self.ui.btnUpdateList.clicked.connect(self.btnUpdateListPressed)

    def btnRemovePressed(self):
        listItems = self.ui.lstIPs.selectedItems()
        if not listItems: return
        for item in listItems:
            self.ui.lstIPs.takeItem(self.ui.lstIPs.row(item))

    def btnAddPressed(self):
        reg_ex = r"^((([0-9])|([1-9][0-9])|(1[0-9][0-9])|(2[0-4][0-9])|(25[0-5]))\.){3}" \
                 r"(([0-9])|([1-9][0-9])|(1[0-9][0-9])|(2[0-4][0-9])|(25[0-5]))$"
        does_match = re.compile(reg_ex).match
        if does_match(self.ui.ip_name.text()):
            self.ui.lstIPs.addItem(self.ui.ip_name.text())
        else:
            self.ui.ip_name.setText("ip format is wrong. please use _._._._ format")

    def btnUpdateListPressed(self):
        self.close()

    def closeEvent(self, event: QCloseEvent) -> None:
        self.parent.ips = sorted([self.ui.lstIPs.item(i).text() for i in range(self.ui.lstIPs.count())])
        self.parent.update_table()


class Tracert(QDialog):
    def __init__(self, parent=None, ips=[]):
        super().__init__()
        self.ui = Tracert_design.Ui_Form()
        self.ui.setupUi(self)
        result = [subprocess.check_output(f"tracert {i}") for i in ips]
        for i in result:
            self.ui.txtTracert.insertPlainText(str(i))


if __name__ == "__main__":
    app = QApplication(sys.argv)

    myWindow = Monitor()
    myWindow.show()

    sys.exit(app.exec_())