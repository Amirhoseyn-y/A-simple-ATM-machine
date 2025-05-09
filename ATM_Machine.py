import sys
import json
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QStackedWidget, QVBoxLayout, QLineEdit,
    QPushButton, QLabel, QMessageBox, QFormLayout
)
from PyQt6.QtCore import Qt

DATA_FILE = 'users.json'

def load_users():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w') as f:
            json.dump({}, f)
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(DATA_FILE, 'w') as f:
        json.dump(users, f, indent=4)

users = load_users()

class RegisterPage(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        layout = QFormLayout()
        self.card_input = QLineEdit()
        self.pin_input = QLineEdit()
        self.pin_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.balance_input = QLineEdit()
        self.register_btn = QPushButton("Register")
        self.register_btn.clicked.connect(self.register)
        self.back_btn = QPushButton("Back to Login")
        self.back_btn.clicked.connect(lambda: parent.setCurrentIndex(0))
        layout.addRow("Card Number:", self.card_input)
        layout.addRow("PIN:", self.pin_input)
        layout.addRow("Initial Balance:", self.balance_input)
        layout.addRow(self.register_btn)
        layout.addRow(self.back_btn)
        self.setLayout(layout)
    def register(self):
        card = self.card_input.text()
        pin = self.pin_input.text()
        try:
            balance = int(self.balance_input.text())
        except:
            QMessageBox.warning(self, "Error", "Invalid balance amount")
            return
        if card in users:
            QMessageBox.warning(self, "Error", "Card number already exists")
        else:
            users[card] = {'pin': pin, 'balance': balance}
            save_users(users)
            QMessageBox.information(self, "Success", "Account created successfully")
            self.parent.setCurrentIndex(0)

class LoginPage(QWidget):
    def __init__(self, parent, app):
        super().__init__()
        self.parent = parent
        self.app = app
        layout = QVBoxLayout()
        self.card_input = QLineEdit()
        self.pin_input = QLineEdit()
        self.pin_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.login_btn = QPushButton("Login")
        self.login_btn.clicked.connect(self.check_login)
        self.register_btn = QPushButton("Register")
        self.register_btn.clicked.connect(lambda: parent.setCurrentIndex(6))
        layout.addWidget(QLabel("Card Number:"))
        layout.addWidget(self.card_input)
        layout.addWidget(QLabel("PIN:"))
        layout.addWidget(self.pin_input)
        layout.addWidget(self.login_btn)
        layout.addWidget(self.register_btn)
        self.setLayout(layout)
    def check_login(self):
        card = self.card_input.text()
        pin = self.pin_input.text()
        if card in users and users[card]['pin'] == pin:
            self.app.current_user = card
            self.parent.setCurrentIndex(1)
        else:
            QMessageBox.warning(self, "Error", "Incorrect card number or PIN")

class MenuPage(QWidget):
    def __init__(self, parent, app):
        super().__init__()
        self.parent = parent
        self.app = app
        layout = QVBoxLayout()
        layout.addWidget(QLabel("ATM Main Menu"))
        buttons = [
            ("Check Balance", self.show_balance),
            ("Withdraw", lambda: parent.setCurrentIndex(2)),
            ("Transfer", lambda: parent.setCurrentIndex(3)),
            ("Change PIN", lambda: parent.setCurrentIndex(4)),
            ("Logout", lambda: parent.setCurrentIndex(0))
        ]
        for text, func in buttons:
            btn = QPushButton(text)
            btn.clicked.connect(func)
            layout.addWidget(btn)
        self.setLayout(layout)
    def show_balance(self):
        user = self.app.current_user
        QMessageBox.information(self, "Balance", f"Your balance is: {users[user]['balance']} Toman")

class WithdrawPage(QWidget):
    def __init__(self, parent, app):
        super().__init__()
        self.parent = parent
        self.app = app
        layout = QFormLayout()
        self.amount_input = QLineEdit()
        self.withdraw_btn = QPushButton("Withdraw")
        self.withdraw_btn.clicked.connect(self.withdraw)
        self.back_btn = QPushButton("Back")
        self.back_btn.clicked.connect(lambda: parent.setCurrentIndex(1))
        layout.addRow("Amount:", self.amount_input)
        layout.addRow(self.withdraw_btn)
        layout.addRow(self.back_btn)
        self.setLayout(layout)
    def withdraw(self):
        user = self.app.current_user
        amount = int(self.amount_input.text())
        if amount <= users[user]['balance']:
            users[user]['balance'] -= amount
            save_users(users)
            QMessageBox.information(self, "Success", f"Withdrawn {amount} Toman")
        else:
            QMessageBox.warning(self, "Error", "Insufficient balance")
        self.parent.setCurrentIndex(1)

class TransferPage(QWidget):
    def __init__(self, parent, app):
        super().__init__()
        self.parent = parent
        self.app = app
        layout = QFormLayout()
        self.target_input = QLineEdit()
        self.amount_input = QLineEdit()
        self.transfer_btn = QPushButton("Transfer")
        self.transfer_btn.clicked.connect(self.transfer)
        self.back_btn = QPushButton("Back")
        self.back_btn.clicked.connect(lambda: parent.setCurrentIndex(1))
        layout.addRow("Target Card:", self.target_input)
        layout.addRow("Amount:", self.amount_input)
        layout.addRow(self.transfer_btn)
        layout.addRow(self.back_btn)
        self.setLayout(layout)
    def transfer(self):
        user = self.app.current_user
        target = self.target_input.text()
        try:
            amount = int(self.amount_input.text())
        except:
            QMessageBox.warning(self, "Error", "Invalid amount")
            return

        if target not in users:
            QMessageBox.warning(self, "Error", "Target card does not exist")
        elif amount > users[user]['balance']:
            QMessageBox.warning(self, "Error", "Insufficient balance")
        else:
            users[user]['balance'] -= amount
            users[target]['balance'] += amount
            save_users(users)
            QMessageBox.information(self, "Success", f"Transferred {amount} Toman to {target}")
        self.parent.setCurrentIndex(1)

class ChangePinPage(QWidget):
    def __init__(self, parent, app):
        super().__init__()
        self.parent = parent
        self.app = app
        layout = QFormLayout()
        self.old_pin_input = QLineEdit()
        self.old_pin_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_pin_input = QLineEdit()
        self.new_pin_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.change_btn = QPushButton("Change PIN")
        self.change_btn.clicked.connect(self.change_pin)
        self.back_btn = QPushButton("Back")
        self.back_btn.clicked.connect(lambda: parent.setCurrentIndex(1))
        layout.addRow("Old PIN:", self.old_pin_input)
        layout.addRow("New PIN:", self.new_pin_input)
        layout.addRow(self.change_btn)
        layout.addRow(self.back_btn)
        self.setLayout(layout)
    def change_pin(self):
        user = self.app.current_user
        if self.old_pin_input.text() == users[user]['pin']:
            users[user]['pin'] = self.new_pin_input.text()
            save_users(users)
            QMessageBox.information(self, "Success", "PIN changed successfully")
            self.parent.setCurrentIndex(1)
        else:
            QMessageBox.warning(self, "Error", "Incorrect old PIN")

class ATMApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ATM Machine - PyQt6")
        self.setFixedSize(300, 300)
        self.current_user = None
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        self.login_page = LoginPage(self.stack, self)
        self.menu_page = MenuPage(self.stack, self)
        self.withdraw_page = WithdrawPage(self.stack, self)
        self.transfer_page = TransferPage(self.stack, self)
        self.change_pin_page = ChangePinPage(self.stack, self)
        self.register_page = RegisterPage(self.stack)
        self.stack.addWidget(self.login_page)
        self.stack.addWidget(self.menu_page)
        self.stack.addWidget(self.withdraw_page)
        self.stack.addWidget(self.transfer_page)
        self.stack.addWidget(self.change_pin_page)
        self.stack.addWidget(QWidget())
        self.stack.addWidget(self.register_page)

def main():
    app = QApplication(sys.argv)
    window = ATMApp()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
