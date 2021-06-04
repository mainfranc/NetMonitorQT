from PySide2.QtCore import Signal, QThread, Qt, QSettings, Slot
from PySide2.QtGui import QCloseEvent, QShowEvent, QHideEvent
from PySide2.QtWidgets import QWidget, QApplication, QDialog, QTableWidgetItem, QMessageBox

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
        self.prev_run_status = False
        # settings
        self.settings = QSettings('Monitor')
        self.ips = sorted(self.load_data())
        # Thread
        self.t = IPsThread()
        self.t.started.connect(lambda: print("Поток запущен"))
        self.t.finished.connect(lambda: print("Поток завершен"))
        self.t.mysignal.connect(self.update_ip_status, Qt.QueuedConnection)

        self.trace_t = TraceThread()
        self.trace_t.mysignal.connect(self.btnTracertPressed, Qt.QueuedConnection)
        # button clicks
        self.ui.btnSettings.clicked.connect(self.btnSettingsPressed)
        self.ui.btnTracert.clicked.connect(self.trace_t.start)
        self.ui.btnStart.clicked.connect(self.t.start)
        self.ui.btnStop.clicked.connect(self.stop)
        # table update
        self.update_table()
        self.ips_status = {i: None for i in self.ips}

    def load_data(self):
        if self.settings.value('ips'):
            return [i for i in self.settings.value('ips')]
        return []

    @Slot()
    def btnSettingsPressed(self):
        setting_window = IPSettings(self, self.ips)
        setting_window.exec_()

    @Slot()
    def btnTracertPressed(self):
        ips_to_search = []
        for index in self.ui.tblIPs.selectedItems():
            ips_to_search.append(self.ui.tblIPs.item(index.row(), 0).text())
        tracert_window = Tracert(self, ips_to_search)
        tracert_window.exec_()

    def update_table(self):
        self.ui.tblIPs.clearContents()
        for row in range(self.ui.tblIPs.rowCount(), -1, -1):
            self.ui.tblIPs.removeRow(row)
        rowPosition = 0
        for i in self.ips:
            self.ui.tblIPs.insertRow(rowPosition)
            self.ui.tblIPs.setItem(rowPosition, 0, QTableWidgetItem(i))
            rowPosition += 1

    def update_ip_status(self):
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
        result = QMessageBox.question(self,
                                      "Exit",
                                      "Do you want to save the changes?",
                                      QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
        if result.name != b"Cancel":
            if result.name == b"Yes":
                self.settings.setValue("ips", self.ips)
            return QWidget.closeEvent(self, event)
        event.ignore()
        return None

    def showEvent(self, event):
        if self.prev_run_status:
            self.t.start()
            print("continue execution")
        return QWidget.showEvent(self, event)

    def hideEvent(self, event):
        self.hide_proc()
        return QWidget.hideEvent(self, event)

    def hide_proc(self):
        if self.t.status:
            self.prev_run_status = self.t.status
            self.stop()
            print("execution paused")

    @Slot()
    def stop(self):
        self.t.status = False
        self.ui.lblstatus.setText("Стоп")


class IPsThread(QThread):
    mysignal = Signal()
    status = False

    def run(self) -> None:
        self.status = True
        while self.status:
            self.mysignal.emit()
            time.sleep(20)

class TraceThread(QThread):
    mysignal = Signal()
    status = False

    def run(self) -> None:
        self.mysignal.emit()
        # time.sleep(5)


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

    @Slot()
    def btnRemovePressed(self):
        listItems = self.ui.lstIPs.selectedItems()
        if not listItems: return
        for item in listItems:
            self.ui.lstIPs.takeItem(self.ui.lstIPs.row(item))

    @Slot()
    def btnAddPressed(self):
        reg_ex = r"^((([0-9])|([1-9][0-9])|(1[0-9][0-9])|(2[0-4][0-9])|(25[0-5]))\.){3}" \
                 r"(([0-9])|([1-9][0-9])|(1[0-9][0-9])|(2[0-4][0-9])|(25[0-5]))$"
        does_match = re.compile(reg_ex).match
        if does_match(self.ui.ip_name.text()):
            self.ui.lstIPs.addItem(self.ui.ip_name.text())
        else:
            self.ui.ip_name.setText("ip format is wrong. please use _._._._ format")

    @Slot()
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
            self.ui.txtTracert.insertPlainText(i.decode('ascii', errors='ignore'))


if __name__ == "__main__":
    app = QApplication(sys.argv)

    myWindow = Monitor()
    myWindow.show()

    sys.exit(app.exec_())