from PyQt6.QtWidgets import (QApplication, QPushButton, QLineEdit, QMainWindow, QDialog, QCheckBox,  QFileDialog, QMessageBox,
                             QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem, QTableWidgetItem, QGraphicsItem)
from PyQt6.QtGui import QPixmap, QBrush, QColor, QPen, QIcon

from Main_Window import Ui_Main
from DataBases import User_Database, Database_With_Users
from Profile import Ui_Profile
from Create_table import Ui_Create_table
from Data import Ui_Data
from Code import Ui_Code

import sys
import os
from PIL import Image
import shutil



class Visual_PO_for_DB(QMainWindow, Ui_Main):
    def __init__(self):
        super().__init__()
        super().setupUi(self)
        self.open_page_login()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('VizSQL')
        self.setWindowIcon(QIcon(resource_path('images/Viz_SQL.png')))
        self.newuser_button_2.clicked.connect(self.open_page_registration)
        self.newuser_button_3.clicked.connect(self.log_in_new_user)
        self.log_in_button.clicked.connect(self.log_in)
        self.return_log_in_button.clicked.connect(self.open_page_login)
        self.users = Database_With_Users()
        self.create_table_window = False
        self.log_out_image_button.setIcon(QIcon(resource_path('images/выход.png')))
        self.add_table_image_button.setIcon(QIcon(resource_path('images/добавить_таблицу.png')))
        self.profile_image_button.setIcon(QIcon(resource_path('images/профиль.png')))
        self.add_database_image_button.setIcon(QIcon(resource_path('images/добавить_бд.png')))
        self.delete_table_image_buttonm.setIcon(QIcon(resource_path('images/удалить_таблицу.png')))
        self.delete_database_image_button.setIcon(QIcon(resource_path('images/удалить_бд.png')))
        self.save_database_image_button.setIcon(QIcon(resource_path('images/сохранить.png')))
        self.code_image_button.setIcon(QIcon(resource_path('images/код.png')))




    '''Главная страница'''
    def open_page_main(self, new_user=False):# Открытие главной страницы
        self.VizSQL.setCurrentIndex(2)
        self.mydatabase_button.clicked.connect(lambda _: self.down_menu.setCurrentIndex(1))
        self.createdatabase_button.clicked.connect(lambda _: self.down_menu.setCurrentIndex(3))
        self.deletedatabase_button.clicked.connect(lambda _: self.down_menu.setCurrentIndex(2))
        self.deletedatabase_button_2.clicked.connect(lambda _: self.down_menu.setCurrentIndex(4))

        self.add_database_image_button.clicked.connect(lambda _: self.down_menu.setCurrentIndex(3))
        self.delete_database_image_button.clicked.connect(lambda _: self.down_menu.setCurrentIndex(2))
        self.delete_table_image_buttonm.clicked.connect(lambda _: self.down_menu.setCurrentIndex(4))
        self.down_menu.setCurrentIndex(0)
        self.directory = f'users/{self.user[2]}'
        if os.listdir(f'{self.directory}/databases'):
            self.user_db = User_Database(self.user[2], os.listdir(f'{self.directory}/databases')[0])
        else:
            self.user_db = User_Database(self.user[2], f'{self.user[2]}.db')
        """Сигналы кнопок"""
        self.download_button.clicked.connect(self.load_database)
        self.Log_out_button.clicked.connect(self.log_out)
        self.createtable_button.clicked.connect(self.open_create_table_windows)
        self.profile_button.clicked.connect(self.open_profile_dialog_window)
        self.save_new_database_button.clicked.connect(self.create_user_databases)
        self.deletedatabase_button_2.clicked.connect(self.open_delete_table_window)
        self.datatable_button.clicked.connect(self.open_data_window)
        self.mydatabase_button.clicked.connect(self.change_database)
        self.deletedatabase_button.clicked.connect(self.delete_database)
        self.save_database.clicked.connect(self.save_as_database)
        self.code_button.clicked.connect(self.open_code_window)

        self.log_out_image_button.clicked.connect(self.log_out)
        self.add_table_image_button.clicked.connect(self.open_create_table_windows)
        self.profile_image_button.clicked.connect(self.open_profile_dialog_window)
        self.add_database_image_button.clicked.connect(self.create_user_databases)
        self.delete_table_image_buttonm.clicked.connect(self.open_delete_table_window)
        self.delete_database_image_button.clicked.connect(self.delete_database)
        self.save_database_image_button.clicked.connect(self.save_as_database)
        self.code_image_button.clicked.connect(self.open_code_window)
        """Создание представления таблиц"""
        if new_user:
            self.update_main_window()

    '''функции для обновления таблиц на гланом экране'''
    def update_main_window(self):
        self.scene = QGraphicsScene(self)
        self.lines = []
        self.graphicsView.setScene(self.scene)
        self.load_tables_from_db()

    def load_tables_from_db(self):
        self.tables = self.user_db.get_tables()
        self.models_table = {}
        for table in self.tables:
            table_name = table[0]
            fields_info = self.user_db.cursor.execute(f'PRAGMA table_info({table_name});').fetchall()
            fields = [f"{info[1]}: {info[2]}" for info in fields_info]
            table_item = TableModelItem(table_name, fields, self)
            self.models_table[table_name] = table_item
            self.scene.addItem(table_item)
            table_item.setPos(20, 20 + 120 * len(self.models_table))
        self.create_connections()

    def create_connections(self):
        for table in self.tables:
            table_name = table[0]
            foreign_keys = self.user_db.get_foreign_keys(table_name)
            for key in foreign_keys:
                if key[2] in self.models_table.keys():
                    self.draw_connection(self.models_table[table_name], self.models_table[key[2]])

    def draw_connection(self, model1, model2):
        line = self.scene.addLine(model1.x() + model1.rect().width() / 2,
                                  model1.y() + model1.rect().height(),
                                  model2.x() + model2.rect().width() / 2,
                                  model2.y(),
                                  QPen(QColor(200, 100, 0), 2))
        self.lines.append(line)

    def update_lines(self):
        for line in self.lines:
            self.scene.removeItem(line)
        self.lines.clear()
        for model1_name, model1 in self.models_table.items():
            foreign_keys = self.user_db.get_foreign_keys(model1_name)
            for key in foreign_keys:
                if key[2] in self.models_table.keys():
                    model2 = self.models_table[key[2]]
                    line = self.scene.addLine(
                        model1.x() + model1.rect().width() / 2,
                        model1.y() + model1.rect().height(),
                        model2.x() + model2.rect().width() / 2,
                        model2.y(),
                        QPen(QColor(200, 100, 0), 2)
                    )
                    self.lines.append(line)

    '''Сохранить базу данных'''
    def save_as_database(self):
        new_directory = QFileDialog.getExistingDirectory(None, 'Выберите директорию')
        old_directory = f'{self.directory}/databases/{self.user_db.get_name()}'
        try:
            shutil.copy2(old_directory, new_directory)
            QMessageBox.warning(self, 'Всё сохраненно', f'База данных {self.user_db.get_name()} сохраннена в выбранный каталог')
            self.update_main_window()
        except Exception:
            QMessageBox.warning(self, 'Ошибка', 'Что-то пошло не так')


    def open_code_window(self):
        self.code_window = Code(self)
        self.code_window.exec()

    '''Данные таблицы'''
    def open_data_window(self):
        self.data_window = Data_Window(self)
        self.data_window.exec()

    '''Выбор базы данных'''
    def change_database(self):
        self.my_data_base_change.clear()
        self.change_check_database.setChecked(False)
        self.my_data_base_change.addItems(os.listdir(f'{self.directory}/databases') if os.listdir(f'{self.directory}/databases') else ['Нет баз данных'])
        self.save_change_database_button.clicked.connect(self.save_and_change_database)

    def save_and_change_database(self):
        if self.change_check_database.isChecked():
            if self.user_db.get_name() != self.my_data_base_change.currentText():
                self.user_db.close()
                self.user_db = User_Database(self.user[2], self.my_data_base_change.currentText())
            self.update_main_window()
            self.down_menu.setCurrentIndex(0)

    '''Удаление Базы данных'''
    def delete_database(self):
        self.my_data_base_change_2.clear()
        self.delete_check_database.setChecked(False)
        self.my_data_base_change_2.addItems(os.listdir(f'{self.directory}/databases') if os.listdir(f'{self.directory}/databases') else ['Нет баз данных'])
        self.delete_button_button_save.clicked.connect(self.save_and_delete_database)
        self.error_delete_database.setText('')

    def save_and_delete_database(self):
        if self.delete_check_database.isChecked():
            if len(os.listdir(f'{self.directory}/databases')) > 1:
                if self.user_db.get_name() == self.my_data_base_change_2.currentText():
                    self.user_db.close()
                    os.remove(f'{self.directory}/databases/{self.user_db.get_name()}')
                    self.user_db = User_Database(self.user[2], os.listdir(f'{self.directory}/databases')[0])
                else:
                    os.remove(f'{self.directory}/databases/{self.my_data_base_change_2.currentText()}')
                self.update_main_window()
                self.down_menu.setCurrentIndex(0)
            else:
                self.error_delete_database.setText('Нельзя удалить(так как она последняя)')
        else:
            self.error_delete_database.setText('Нажатие на квадратик обязательно')

    '''Удаление таблицы'''
    def open_delete_table_window(self):
        self.delete_check.setChecked(False)
        self.name_used_database_delete_table.setText(self.user_db.get_name())
        self.label_25.setText('')
        tables = [i[0] for i in self.user_db.get_tables()]
        self.table_delete.clear()
        if tables:
            self.table_delete.addItems(tables)
        else:
            self.table_delete.addItems(['Нет доступных таблиц'])
        self.delete_and_save_table.clicked.connect(self.delete_and_save_button)

    def delete_and_save_button(self):
        name = self.table_delete.currentText()
        if self.delete_check.isChecked():
            if self.user_db.delete_table(name):
                self.update_main_window()
                self.down_menu.setCurrentIndex(0)
        else:
            self.label_25.setText('Нажмите на квадратик')

    '''Открытие новой базы данных'''
    def load_database(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите файл", "",
                                                       "Database Files (*.db);;All Files (*)")
        if file_path:
           file_name = os.path.splitext(os.path.basename(file_path))[0]
           self.load_database_2(file_name, file_path)

    def load_database_2(self, file_name, file_path):
        try:
            if os.path.exists(os.path.join(self.directory + '/databases', file_name + '.db')):
                score = 0
                while os.path.exists(os.path.join(self.directory + '/databases', file_name + f'_{score}.db')):
                    score += 1
                os.rename(file_path, os.path.join(self.directory + '/databases', file_name + f'_{score}.db'))
                file_name = file_name + f'_{score}'
            else:
                os.rename(file_path, os.path.join(self.directory + '/databases', file_name + f'.db'))
            self.user_db.close()
            self.user_db = User_Database(self.user[2], file_name + '.db')
            self.update_main_window()
        except:
            QMessageBox.warning(self, 'Ошибка', 'Что-то пошло не так')

    '''Создание новой базы данных'''

    def create_user_databases(self):
        self.error_create_database_text.setVisible(False)
        log_in_except = {lambda: self.check_new_database.isChecked(): 'Нажатие на квадратик обязательное условие',
                         lambda: self.name_new_database.text(): 'Название должно быть больше 4 символов и содержать буквы и цифры',
                         lambda: not os.path.exists(f'{self.directory}/databases/{self.name_new_database.text()}.db'): 'База данных с таким названием уже существует',
                         }
        text_except = self.return_text_exception(log_in_except)
        if text_except:
            self.error_create_database_text.setVisible(True)
            self.error_create_database_text.setText(text_except)
        else:
            self.user_db.close()
            self.user_db = User_Database(self.user[2], self.name_new_database.text() + '.db')
            QMessageBox.information(self, "Создание завершено", f"База данных {self.name_new_database.text()} создана")
            self.name_new_database.setText('')
            self.check_new_database.setChecked(False)
            self.down_menu.setCurrentIndex(0)
            self.update_main_window()

    '''Окно для создания таблицы'''

    def open_create_table_windows(self):
        self.open_add_table_window = Create_Table(self)
        self.open_add_table_window.exec()

    '''Окно Профиля'''

    def open_profile_dialog_window(self):
        self.profile_window = Profile(self)
        self.profile_window.exec()

    '''Функции авторизозации пользователя'''

    def open_page_login(self):
        self.VizSQL.setCurrentIndex(0)
        self.login.setText('')
        self.password.setText('')
        self.error_Log_in_text.setVisible(False)
        self.user_db = None
        self.user = None

    def open_page_registration(self):
        self.newuser_name.setText('')
        self.newuser_login.setText('')
        self.newuser_password_2.setText('')
        self.VizSQL.setCurrentIndex(1)
        self.newuser_error_text.setVisible(False)

    def log_in(self):# Вход в существующий аккаунт
        log_in_except = {lambda: len(self.login.text()) > 7 and not self.login.text().isdigit()
                                 and not self.login.text().isalpha(): 'Логин должен быть не чем из менее 8 символов \n и состоять из букв и цифр',
                       lambda: len(self.password.text()) > 5 and not self.password.text().isdigit()
                                 and not self.password.text().isalpha(): 'Пароль должен быть не менее чем 6 символов \n и состоять из букв и цифр',
                       lambda: self.users.find_user(self.login.text(), self.password.text()): 'Пользователь не найден',
                       }
        text_except = self.return_text_exception(log_in_except)
        if text_except:
            self.error_Log_in_text.setVisible(True)
            self.error_Log_in_text.setText(text_except)
        else:
            self.user = self.users.find_user(self.login.text(), self.password.text())
            self.open_page_main(True)

    def log_out(self):
        self.user_db.close()
        self.open_page_login()

    def log_in_new_user(self):# Функция для регистрации нового пользователя
        log_in_except = {lambda: len(self.newuser_name.text()) > 4: 'Имя должно быть не чем из менее 5 символов',
                         lambda: len(self.newuser_login.text()) > 7 and not self.newuser_login.text().isdigit()
                                 and not self.newuser_login.text().isalpha(): 'Логин должен быть не чем из менее 8 символов \n и состоять из букв и цифр',
                         lambda: len(self.newuser_password_2.text()) > 5 and not self.newuser_password_2.text().isdigit() and not self.newuser_password_2.text().isalpha(): 'Пароль должен быть не менее чем 6 символов \n и состоять из букв и цифр',
                         lambda: self.CHECK.isChecked(): 'Нажатие на квадратик обязательное условие',
                         lambda: self.users.add_user(self.newuser_name.text(), self.newuser_login.text(), self.newuser_password_2.text()): 'Пользователь с таким логином уже существует',
                         }

        text_except = self.return_text_exception(log_in_except)
        if text_except:
            self.newuser_error_text.setText(text_except)
            self.newuser_error_text.setVisible(True)
        else:
            self.user = self.users.find_user(self.newuser_login.text(), self.newuser_password_2.text())
            self.create_users_directory()
            self.open_page_main(True)

    def create_users_directory(self):# Создание собственной директории для пользователя
        os.makedirs(f'{os.getcwd()}/users/{self.user[2]}')
        os.makedirs(f'{os.getcwd()}/users/{self.user[2]}/databases')
        os.makedirs(f'{os.getcwd()}/users/{self.user[2]}/image_profile')
        os.makedirs(f'{os.getcwd()}/users/{self.user[2]}/code')

    '''Различные функции для более удобной работы с приложением'''
    def return_text_exception(self, dict_except):# Возвращает текс ошибки если такая есть
        for exception, text in dict_except.items():
            try:
                if not exception():
                    return text
            except Exception as d:
                pass
        return False


class TableModelItem(QGraphicsRectItem):# Модель представления таблицы
    def __init__(self, table_name, pols, main_window):
        size1 = len(max(pols, key=lambda s: len(s))) * 10
        size2 = 60 + 20 * len(pols)
        super().__init__(0, 0, size1, size2)
        self.setBrush(QBrush(QColor(200, 200, 255)))
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.table_title = QGraphicsTextItem(table_name, self)
        self.table_title.setPos(size1 // 2 - 5 * len(table_name), 10)
        self.mainWindow = main_window

        for i, pole in enumerate(pols):
            pole_text = QGraphicsTextItem(pole, self)
            pole_text.setPos(size1 // 2 - 4 * len(pole), 30 + i * 20)

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            self.mainWindow.update_lines()
        return super().itemChange(change, value)


class Profile(QDialog, Ui_Profile):
    def __init__(self, main_window):
        super().__init__()
        super().setupUi(self)
        self.setWindowIcon(QIcon(resource_path('images/профиль.png')))
        self.setWindowTitle('Профиль')
        self.change_image_button.clicked.connect(self.change_and_save_image_profile)
        self.save_create_pole.clicked.connect(self.save_and_close_profile_windows)
        self.main_window = main_window
        if not os.listdir(f'{self.main_window.directory}/image_profile/'):
            self.profile_image.setText('Нет изображения')
        else:
            image = QPixmap(f'{self.main_window.directory}/image_profile/image_profile.png')
            self.profile_image.setPixmap(image)
        self.name_profile_text.setText(f'Здравствуйте, {self.main_window.user[1]}!')
        self.name_login_text.setText(f'{self.main_window.user[2]}')

    def change_and_save_image_profile(self):  # Выбрать картинку у профиля
        image = QFileDialog.getOpenFileName(self, 'Выбрать картинку', '')[0]
        if image:
            try:
                img = Image.open(image).resize((250, 250))
                save_path = os.path.join(f'{self.main_window.directory}/image_profile', 'image_profile.png')
                img.save(save_path)
                image = QPixmap(save_path)
                self.profile_image.setPixmap(image)
            except IOError:
                QMessageBox.warning(self, "Ошибка", "Выбранный файл не является изображением.")
        else:
            QMessageBox.warning(self, "Ошибка", "Файл не выбран.")

    def save_and_close_profile_windows(self):  # Закрыть окно профиля
        self.main_window.users.update_name_users(self.user_name_profile.text(), self.main_window.user[0])
        self.user = self.main_window.users.find_user(self.main_window.user[2], self.main_window.user[3])
        self.main_window.update_main_window()
        self.close()


class Create_Table(QDialog, Ui_Create_table):
    def __init__(self, main_window):# Открытие окна
        super().__init__()
        super().setupUi(self)
        self.setWindowTitle('Создание таблицы')
        self.setWindowIcon(QIcon('images/добавить_таблицу.png'))
        self.main_window = main_window
        self.PrimaryKey_Button.toggled.connect(self.choose_primary_key)
        self.ForeignKey_Button_2.toggled.connect(self.choose_foreign_key)
        self.save_create_pole_button.clicked.connect(self.create_pole_in_tables)
        self.save_create_table_button.clicked.connect(self.save_and_close_create_table_windows)
        self.save_create_pole_button.clicked.connect(self.create_pole)
        self.Not_Key.toggled.connect(self.choose_not_key)
        self.table_with_pole.clear()
        self.table_with_pole.setRowCount(0)
        self.name_table.setText('')
        self.name_pole.setText('')
        self.type_pole.clear()
        self.name_used_database.setText(f'{self.main_window.user_db.get_name()}')
        self.table_with_pole.setColumnCount(13)
        self.table_with_pole.setHorizontalHeaderLabels(
                ['название', 'тип', 'ключ', 'AutoIncrement', 'Binary', 'Not Null', 'Unsignet', 'Uniqure', 'Zero Fill',
                 'По умолчанию', 'Таблица 1 ключа', 'поле 1 ключа', 'Удалить'])
        self.type_pole.addItems(["INTEGER", "TEXT", "REAL"])
        self.Not_Key.setChecked(True)
        self.error_create_table.setVisible(False)
        self.pols = []
        self.key = False

    def create_pole_in_tables(self):# Создание нового поля у таблицы


        def check_true(signal):# Быстрая обработка False и True
            return 'да' if signal else 'нет'


        if self.name_pole.text():
            if not list(filter(lambda s: s['название'] == self.name_pole.text(), self.pols)):
                self.table_with_pole.setRowCount(self.table_with_pole.rowCount() + 1)
                dict_pole = {'название': self.name_pole.text(),
                             'тип': self.type_pole.currentText(),
                             'ключ': self.key,
                             'AutoIncrement': self.AutoIncrement.isChecked(),
                             'Binary': self.Binary.isChecked(),
                             'Not Null': self.NotNull.isChecked(),
                             'Unsignet': self.Unsignet.isChecked(),
                             'Uniqure': self.Uniqure.isChecked(),
                             'Zero Fill': self.Zerofill.isChecked(),
                             'Default': self.Defaut.text(),
                             'Таблица первичного ключа': self.table_ForeignKey.currentText() if self.key == 'Вторичный' else False,
                             'Поле первичного ключа': self.pole_ForeignKey.currentText() if self.key == 'Вторичный' else False,
                             }
                keys = list(dict_pole.keys())
                self.pols.append(dict_pole)
                for i in range(12):
                    a = check_true(dict_pole[keys[i]]) if dict_pole[keys[i]] in [True, False] else dict_pole[keys[i]]
                    try:
                        item = QLineEdit()
                        item.setText(a)
                        item.setEnabled(False)
                        self.table_with_pole.setCellWidget(self.table_with_pole.rowCount() - 1, i, item)
                    except Exception as d:
                        pass
                try:
                    button = QPushButton()
                    button.setText('Удалить')
                    button.clicked.connect(lambda _: self.delete_pole(dict_pole['название']))
                    self.table_with_pole.setCellWidget(self.table_with_pole.rowCount() - 1, 12, button)
                except Exception as s:
                    pass
            else:
                self.error_create_table.setVisible(True)
                self.error_create_table.setText('Некорректное имя поля')
        else:
            self.error_create_table.setVisible(True)
            self.error_create_table.setText('Некорректное имя поля')



    def delete_pole(self, name):# Удаление поля у новой таблицы
        for i in range(len(self.pols)):
            if self.pols[i]['название'] == name:
                self.table_with_pole.removeRow(i)
                del self.pols[i]
                break



    def choose_not_key(self):# Выбор(Поле это не ключ)
        try:
            self.key = False
            self.type_pole.clear()
            self.pole_ForeignKey.clear()
            self.table_ForeignKey.clear()
            self.type_pole.addItems(["INTEGER", "TEXT", "REAL"])
            self.NotNull.setChecked(False)
            self.Uniqure.setChecked(False)
            self.NotNull.setEnabled(True)
            self.Uniqure.setEnabled(True)
            self.Binary.setEnabled(True)
            self.Zerofill.setEnabled(True)
            self.Unsignet.setEnabled(True)
            self.table_ForeignKey.setEnabled(False)
            self.pole_ForeignKey.setEnabled(False)
        except Exception as f:
            pass

    def choose_primary_key(self):# Выбор(Поле это первичный ключ)
        try:
            self.key = 'Первичный'
            self.pole_ForeignKey.clear()
            self.type_pole.clear()
            self.table_ForeignKey.clear()
            self.type_pole.addItems(["INTEGER"])
            self.table_ForeignKey.setEnabled(False)
            self.pole_ForeignKey.setEnabled(False)
            self.NotNull.setChecked(True)
            self.Uniqure.setChecked(True)
            self.NotNull.setEnabled(False)
            self.Uniqure.setEnabled(False)
            self.Binary.setEnabled(False)
            self.Zerofill.setEnabled(False)
            self.Unsignet.setEnabled(False)
        except Exception as f:
            pass

    def choose_foreign_key(self):# Выбор(Поле это вторичный ключ)
        try:
            self.key = 'Вторичный'
            self.table_ForeignKey.setEnabled(True)
            self.pole_ForeignKey.setEnabled(True)
            self.type_pole.clear()
            self.type_pole.addItems(["INTEGER"])
            self.table_ForeignKey.clear()
            table = [i[0] for i in self.main_window.user_db.get_tables()]
            self.table_ForeignKey.addItems(table if table else ['нет таблиц'])
            self.table_ForeignKey.currentIndexChanged.connect(self.choose_table_PK)
            self.NotNull.setChecked(True)
            self.Uniqure.setChecked(True)
            self.NotNull.setEnabled(False)
            self.Uniqure.setEnabled(False)
            self.Binary.setEnabled(False)
            self.Zerofill.setEnabled(False)
            self.Unsignet.setEnabled(False)
        except Exception as f:
            pass

    def choose_table_PK(self):# Добавление выбора зависимого поля для вторичного ключа при выборе зависимой таблицы
        try:
            self.pole_ForeignKey.clear()
            primary_keys = self.main_window.user_db.get_primary_key_tables(
                self.table_ForeignKey.currentText())
            self.pole_ForeignKey.addItems(
                primary_keys if primary_keys else ['нет первичных ключей'])
        except Exception as f:
            pass


    def create_pole(self):#
        name_table = self.name_pole.text()

    def save_and_close_create_table_windows(self):# Закрыть окно создания таблицы

        if (self.main_window.user_db.create_table(self.name_table.text(), self.pols) and self.name_table.text() and
                self.table_with_pole.rowCount):
            self.main_window.update_main_window()
            self.close()
        else:
            self.error_create_table.setVisible(True)
            self.error_create_table.setText('Возникла ошибка в добавлении таблицы')


class Data_Window(QDialog, Ui_Data):
    def __init__(self, main_window):
        super().__init__()
        self.setWindowIcon(QIcon(resource_path('images/удалить_бд.png')))
        self.setWindowTitle('Данные')
        super().setupUi(self)
        self.main_window = main_window
        self.error_filter.setText('')
        self.label.setText(f'{self.main_window.user_db.get_name()}')
        self.table.clear()
        self.table.addItems([i[0] for i in self.main_window.user_db.get_tables()])
        self.change_table_button.clicked.connect(self.table_update)
        self.data_pols = None
        self.delete_data_button.clicked.connect(self.delete_pols)
        self.new_data = False
        self.add_data_button_3.clicked.connect(self.add_data_for_table)
        self.clear_sql_button.clicked.connect(lambda _: self.close())
        self.error_add.setText('')
        self.search.clicked.connect(self.search_data)
        self.table_update()
        self.clear.clicked.connect(self.update_table_for_data)


    def search_data(self):
        if self.table.currentText():
            pols = []
            values = []
            for num in range(len(self.head_data)):
                try:
                    if self.filter_pols[num].text():
                        if self.head_data[num][1] == 'INTEGER':
                            value = int(self.filter_pols[num].text())
                        elif self.head_data[num][1] == 'REAL':
                            value = float(self.filter_pols[num].text())
                        else:
                            value = self.filter_pols[num].text()
                        pols.append(self.head_data[num][0])
                        values.append(value)
                except ValueError:
                    self.error_filter.setText('Неккоректные данные')
            data = self.main_window.user_db.search_table_info(self.table_name, pols, values)
            if data:
                self.update_table_for_data(DATA=data)
            else:
                self.error_filter.setText('Нет данных')


    def update_table_for_data(self, DATA=False):
        if self.table.currentText():
            self.error_add.setText('')
            self.error_filter.setText('')
            if not DATA:
                DATA = self.main_window.user_db.data_table(self.table_name)
            self.table_data.clear()
            self.table_data.setHorizontalHeaderLabels(['Выбор'] + [names[0] for names in self.head_data])
            self.table_data.resizeColumnsToContents()
            self.table_data.setRowCount(len(DATA))
            self.data_pols = []

            for row, data1 in enumerate(DATA):
                checkbox = QCheckBox()
                data = {}
                data['check'] = checkbox
                self.table_data.setCellWidget(row, 0, checkbox)
                for col, data2 in enumerate(data1):
                    data[self.head_data[col][0]] = data2
                    data_m = QTableWidgetItem(f'{data2}')
                    self.table_data.setItem(row, col + 1, data_m)
                self.data_pols.append(data)


    def table_update(self):
        if self.table.currentText():
            self.table_name = self.table.currentText()
            self.head_data = self.main_window.user_db.get_info_for_header(self.table.currentText())

            self.table_data.setColumnCount(len(self.head_data) + 1)
            self.filter_table.setColumnCount(2)
            self.filter_table.setHorizontalHeaderLabels(['Поле', 'Значение'])
            self.filter_table.setRowCount(len(self.head_data))
            self.filter_table.resizeColumnsToContents()
            self.filter_pols = []
            for i in range(len(self.head_data)):
                pole = QLineEdit()
                pole.setText(self.head_data[i][0])
                pole.setEnabled(False)
                self.filter_table.setCellWidget(i, 0, pole)
                line_pole = QLineEdit()
                self.filter_table.setCellWidget(i, 1, line_pole)
                self.filter_pols.append(line_pole)
            self.update_table_for_data()


    def delete_pols(self):
        if self.table.currentText():
            delete_pols = []
            if self.data_pols:
                for pole in range(len(self.data_pols)):
                    if self.data_pols[pole]['check'].isChecked():
                        delete_pols.append(pole)
            for i in delete_pols[::-1]:
                self.table_data.removeRow(i)
                del self.data_pols[i]['check']
                self.main_window.user_db.delete_data_for_table(self.table_name, list(self.data_pols[i].keys()),
                                                               list(self.data_pols[i].values()))
                del self.data_pols[i]


    def add_data_for_table(self):
        if self.table.currentText():
            if not self.new_data:
                self.table_data.insertRow(0)
                self.new_data = []
                button_save = QPushButton()
                button_save.setText('Сохранить')
                button_save.clicked.connect(self.save_and_add_data_for_values)
                self.table_data.setCellWidget(0, 0, button_save)
                for i in range(len(self.head_data)):
                    label = QLineEdit()
                    self.new_data.append(label)
                    self.table_data.setCellWidget(0, i + 1, label)


    def save_and_add_data_for_values(self):
        if self.new_data:
            values = []
            for i in range(len(self.new_data)):
                try:
                    if self.head_data[i][1] == 'INTEGER':
                        text = int(self.new_data[i].text())
                    elif self.head_data[i][1] == 'REAL':
                        text = float(self.new_data[i].text())
                    else:
                        text = self.new_data[i].text()
                    values.append(text)
                except ValueError:
                    self.error_add.setText('Ошибка в добавлении данных')
            if len(values) == len(self.new_data):
                self.main_window.user_db.add_data_for_table(self.table_name, values)
                self.new_data = False
                self.update_table_for_data()


class Code(QDialog, Ui_Code):
    def __init__(self, main_window):
        super().__init__()
        super().setupUi(self)
        self.setWindowTitle('Код')
        self.setWindowIcon(QIcon(resource_path('images/код.png')))
        self.main_window = main_window
        file = open(f'users/{self.main_window.user[2]}/code/{self.main_window.user_db.get_name()}.txt', 'r')
        self.code.setText('\n'.join(file.readlines() + ['connection.close()']))
        self.code_button.clicked.connect(lambda _: self.close())

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Visual_PO_for_DB()
    ex.show()
    sys.exit(app.exec())