import sys
import io
import sqlite3

from PIL import Image, ImageFilter
from PIL.ImageQt import ImageQt
from PyQt6.QtGui import QPixmap
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, \
    QInputDialog, QLabel


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('GENERAL_PROJECT.ui', self)
        self.pushButton.clicked.connect(self.clicked)

    def clicked(self):
        fname = QFileDialog.getOpenFileName(self, 'Выбрать картинку', '')[0]
        if fname:
            self.after_click_button = after_click_button(fname)
            self.after_click_button.show()
            self.close()


class after_click_button(QMainWindow):
    def __init__(self, fname):
        super().__init__()
        uic.loadUi('untitled.ui', self)  # Загружаем дизайн

        self.fname = fname

        self.curr_image = Image.open(self.fname)
        self.currr_image = Image.open(self.fname)
        self.size_image = Image.open(self.fname)
        self.very_origin = Image.open(self.fname)

        self.pushButton_undo.clicked.connect(self.bd)
        self.pushButton_redo.clicked.connect(self.bd)
        self.pushButton_RESET.clicked.connect(self.bd)
        self.pushButton_undo.close()
        self.pushButton_redo.close()

        self.con = sqlite3.connect("GENERAL_IMAGE.sqlite3")
        self.cur = self.con.cursor()
        self.cur.execute("""DELETE FROM images""")
        self.con.commit()

        self.current_id = 0

        self.verticalSlider_size.sliderReleased.connect(self.do_action)
        self.verticalSlider_transparency.sliderReleased.connect(self.do_action)
        self.verticalSlider_R.sliderReleased.connect(self.do_action)
        self.verticalSlider_G.sliderReleased.connect(self.do_action)
        self.verticalSlider_B.sliderReleased.connect(self.do_action)

        if self.curr_image.size[0] > self.curr_image.size[1]:
            self.koef = 500 / self.curr_image.size[0]
            self.x = int(self.koef * self.curr_image.size[0])
            self.y = int(self.koef * self.curr_image.size[1])
        else:
            self.koef = 500 / self.curr_image.size[1]
            self.x = int(self.koef * self.curr_image.size[0])
            self.y = int(self.koef * self.curr_image.size[1])

        self.curr_image = self.curr_image.resize((self.x, self.y),
                                                 Image.LANCZOS)
        self.currr_image = self.curr_image

        self.very_origin = self.curr_image.copy()

        self.curr_image.putalpha(0)
        self.curr_image = self.currr_image.resize(
            (int(self.x * 1 / 100), int(self.y * 1 / 100)),
            Image.LANCZOS)

        self.image = ImageQt(self.curr_image)
        self.pixmap = QPixmap.fromImage(self.image)

        self.image2 = QLabel(self)
        self.image2.move(50, 50)
        self.image2.resize(self.x, self.y)
        self.image2.setPixmap(self.pixmap)
        self.image2.setStyleSheet('background-color: rgba(2, 2, 2, 0)')

        self.verticalSlider_transparency.setMaximum(255)
        self.verticalSlider_R.setMaximum(255)
        self.verticalSlider_G.setMaximum(255)
        self.verticalSlider_B.setMaximum(255)
        self.verticalSlider_transparency.valueChanged[int].connect(self.slider_transparency)
        self.verticalSlider_R.valueChanged[int].connect(self.slider_R)
        self.verticalSlider_G.valueChanged[int].connect(self.slider_G)
        self.verticalSlider_B.valueChanged[int].connect(self.slider_B)

        self.verticalSlider_size.setMinimum(1)
        self.verticalSlider_size.valueChanged[int].connect(self.slider_resize)

        self.pushButton_applyFilters.clicked.connect(self.clicked_filters)
        self.pushButton_applyCores.clicked.connect(self.viniet)
        self.pushButton_saveALL.clicked.connect(self.save_all)
        self.pushButton_crop.clicked.connect(self.obrezka)

        self.do_action()  # сохранение первой картинки

    def slider_resize(self, value):  # изменение размера картинки
        self.curr_image = self.currr_image.resize(
            (int(self.x * value / 100), int(self.y * value / 100)),
            Image.LANCZOS)

        self.pixmap = QPixmap.fromImage(ImageQt(self.curr_image))
        self.image2.setPixmap(self.pixmap)

    def slider_transparency(self, value):  # изменение прозрачности
        self.currr_image = self.currr_image.convert('RGB')
        self.curr_image = self.curr_image.convert('RGB')

        self.curr_image.putalpha(value)
        self.currr_image.putalpha(value)
        self.pixmap = QPixmap.fromImage(ImageQt(self.curr_image))
        self.image2.setPixmap(self.pixmap)

    def clicked_filters(self):
        if self.comboBox.currentText() == 'black and white':
            self.curr_image = self.curr_image.convert("L")

        if self.comboBox.currentText() == 'create water mark/logo':
            self.curr_image = self.curr_image.convert("L")
            threshold = 50
            self.curr_image = self.curr_image.point(
                lambda x: 255 if x > threshold else 0)
            self.curr_image = self.curr_image.resize(
                (self.curr_image.width // 2, self.curr_image.height // 2)
            )
            self.curr_image = self.curr_image.filter(ImageFilter.CONTOUR)

        if self.comboBox.currentText() == 'vertical reflection':
            pixels = self.curr_image.load()  # список с пикселями
            x, y = self.curr_image.size  # ширина (x) и высота (y) изображения
            im1 = Image.new("RGB", (x, y), (0, 255, 0))
            for i in range(x, 0, -1):
                for j in range(y, 0, -1):
                    im1.putpixel((x - i, j - 1), (pixels[i - 1, j - 1]))
            self.curr_image = im1

        if self.comboBox.currentText() == 'diagonal reflection':
            pixels = self.curr_image.load()  # список с пикселями
            x, y = self.curr_image.size  # ширина (x) и высота (y) изображения
            im1 = Image.new("RGB", (y, x), (0, 255, 0))
            for i in range(x, 0, -1):
                for j in range(y, 0, -1):
                    im1.putpixel((i - 1, j - 1), (pixels[y - j, x - i]))
            self.curr_image = im1

        if self.comboBox.currentText() == 'show better edges':
            self.curr_image = self.curr_image.filter(ImageFilter.SMOOTH)
            self.curr_image = self.curr_image.filter(ImageFilter.FIND_EDGES)

        if self.comboBox.currentText() == 'show edges':
            self.curr_image = self.curr_image.filter(ImageFilter.FIND_EDGES)

        if self.comboBox.currentText() == 'viniet':
            for i in range(4):
                if self.curr_image.mode != 'RGBA':
                    self.curr_image = self.curr_image.convert('RGBA')
                width, height = self.curr_image.size

                alpha_gradient = Image.new('L', (width, 1), color=0xFF)
                for x in range(width):
                    a = int((0.3 * 255.) * (
                            1. - 3 * float(x) / width))
                    if a > 0:
                        alpha_gradient.putpixel((x, 0), a)
                    else:
                        alpha_gradient.putpixel((x, 0), 0)
                alpha = alpha_gradient.resize(self.curr_image.size)

                black_im = Image.new('RGBA', (width, height),
                                     color=0)
                black_im.putalpha(alpha)

                output_im = Image.alpha_composite(self.curr_image, black_im)
                self.curr_image = output_im

                self.curr_image = self.curr_image.rotate(90)

        if self.comboBox.currentText() == 'gaussian blur':
            age, ok_pressed = QInputDialog.getInt(
                self, "степень размытия", "Введите степень размытия",
                20, 0, 100, 1)
            if ok_pressed:
                self.curr_image = self.curr_image.filter(
                    ImageFilter.GaussianBlur(age))

        if self.comboBox.currentText() == 'blur':
            age, ok_pressed = QInputDialog.getInt(
                self, "степень размытия", "Введите степень размытия",
                20, 0, 100, 1)
            if ok_pressed:
                self.curr_image = self.curr_image.filter(
                    ImageFilter.BoxBlur(age))

        if self.comboBox.currentText() == 'glitch':
            if self.curr_image.mode != 'RGB':
                self.curr_image = self.curr_image.convert('RGB')
            delta, ok_pressed = QInputDialog.getInt(
                self, "степень глитча", "Введите степень глитча",
                20, 0, 100, 1)
            if ok_pressed:

                pixels = self.curr_image.load()
                x, y = self.curr_image.size
                im2 = Image.new("RGB", (x, y), (0, 0, 0))
                im2.paste(self.curr_image)
                for i in range(x):
                    for j in range(y):
                        r, g, b = pixels[i, j]
                        pixels[i, j] = 0, g, b
                pixels1 = im2.load()
                x, y = im2.size
                for i in range(x):
                    for j in range(y):
                        r, g, b = pixels1[i, j]
                        pixels1[i, j] = r, 0, 0
                pixels2 = self.curr_image.load()
                x, y = self.curr_image.size
                for i in range(x):
                    for j in range(y):
                        if i + delta < x:
                            r, g, b = pixels[i + delta, j]
                            r1, g1, b1 = pixels1[i, j]
                            pixels2[i + delta, j] = r1, g, b

        self.pixmap = QPixmap.fromImage(ImageQt(self.curr_image))
        self.image2.setPixmap(self.pixmap)

        self.currr_image = self.curr_image

        self.do_action()

    def slider_R(self, value):
        self.curr_image = self.curr_image.convert('RGB')

        pixels = self.curr_image.load()  # список с пикселями
        x, y = self.curr_image.size

        for i in range(x):
            for j in range(y):
                r, g, b = pixels[i, j]
                r = value
                pixels[i, j] = r, g, b

        self.currr_image = self.curr_image.copy()
        self.pixmap = QPixmap.fromImage(ImageQt(self.curr_image))
        self.image2.setPixmap(self.pixmap)

    def slider_G(self, value):
        self.curr_image = self.curr_image.convert('RGB')

        pixels = self.curr_image.load()  # список с пикселями
        x, y = self.curr_image.size

        for i in range(x):
            for j in range(y):
                r, g, b = pixels[i, j]
                g = value
                pixels[i, j] = r, g, b

        self.currr_image = self.curr_image.copy()
        self.pixmap = QPixmap.fromImage(ImageQt(self.curr_image))
        self.image2.setPixmap(self.pixmap)

    def slider_B(self, value):
        self.curr_image = self.curr_image.convert('RGB')

        pixels = self.curr_image.load()  # список с пикселями
        x, y = self.curr_image.size

        for i in range(x):
            for j in range(y):
                r, g, b = pixels[i, j]
                b = value
                pixels[i, j] = r, g, b

        self.currr_image = self.curr_image.copy()
        self.pixmap = QPixmap.fromImage(ImageQt(self.curr_image))
        self.image2.setPixmap(self.pixmap)

    def viniet(self):
        name, ok_pressed = QInputDialog.getText(self, "Значения ядер",
                                                "Введите через пробел значения ядер")
        if ok_pressed:
            name = list(map(lambda x: float(x), name.split()))

            self.curr_image = self.curr_image.filter(ImageFilter.Kernel((3, 3), (
                name[0], name[1], name[2], name[3], name[4], name[5], name[6],
                name[7],
                name[8]), 1, 0))

            self.currr_image = self.curr_image.copy()
            self.pixmap = QPixmap.fromImage(ImageQt(self.curr_image))
            self.image2.setPixmap(self.pixmap)

            self.do_action()

    def do_action(self):
        self.current_id += 1

        if len(self.cur.execute("""SELECT * FROM images""").fetchall()) == 0:
            self.pushButton_undo.close()
            self.pushButton_redo.close()
        else:
            self.pushButton_undo.show()
            self.pushButton_redo.show()

        roi_img = self.curr_image
        img_byte_arr = io.BytesIO()
        roi_img.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()

        self.cur.execute("""INSERT INTO images
                                  (image)
                                  VALUES
                                  (?)""", (img_byte_arr,)).fetchall()

        self.con.commit()

    def bd(self):

        lage = len(self.cur.execute("""SELECT * FROM images""").fetchall())

        if lage == 0:
            self.pushButton_undo.close()
            self.pushButton_redo.close()
        else:
            self.pushButton_undo.show()
            self.pushButton_redo.show()
            if self.sender().text() == '<-    undo':
                if self.current_id - 1 >= 1:
                    result = self.cur.execute(
                        """SELECT image FROM images WHERE id = ?""",
                        (self.current_id - 1,)).fetchall()

                    img = Image.open(io.BytesIO(result[0][0]))

                    self.pixmap = QPixmap.fromImage(ImageQt(img))
                    self.curr_image = img
                    self.currr_image = img
                    self.image2.setPixmap(self.pixmap)
                    self.current_id -= 1
            elif self.sender().text() == 'RESET ALL':
                self.pixmap = QPixmap.fromImage(ImageQt(self.very_origin))
                self.curr_image = self.very_origin
                self.currr_image = self.very_origin
                self.image2.setPixmap(self.pixmap)
            else:
                if self.current_id + 1 <= lage:
                    result = self.cur.execute(
                        """SELECT image FROM images WHERE id = ?""",
                        (self.current_id + 1,)).fetchall()

                    img = Image.open(io.BytesIO(result[0][0]))

                    self.pixmap = QPixmap.fromImage(ImageQt(img))
                    self.curr_image = img
                    self.currr_image = img
                    self.image2.setPixmap(self.pixmap)
                    self.current_id += 1

    def save_all(self):
        roi_img = self.curr_image
        img_byte_arr = io.BytesIO()
        roi_img.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()

        QFileDialog.saveFileContent(img_byte_arr)

    def obrezka(self):
        self.after_click_obrezka = after_click_obrezka(self.curr_image,
                                                       self.con, self.image2,
                                                       self.current_id, self)
        self.after_click_obrezka.show()


class after_click_obrezka(QMainWindow):
    def __init__(self, image, base, pix, id, lake):
        super().__init__()

        self.rod = base
        self.rod_pix = pix
        self.id = id

        uic.loadUi('after obrezka.ui', self)  # Загружаем дизайн
        # Обратите внимание: имя элемента такое же как в QTDesigner

        self.image = image
        self.lake = lake
        self.image = ImageQt(image)
        self.pixmap = QPixmap.fromImage(self.image)

        self.image2 = QLabel(self)
        self.image2.move(10, 10)
        self.x, self.y = image.size[0], image.size[1]

        self.image2.resize(self.x, self.y)
        self.image2.setPixmap(self.pixmap)

        self.image2.setStyleSheet('background-color: rgba(2, 2, 2, 0)')
        self.label_5.setText(
            'X between 0 and ' + str(self.x) + '\nY between 0 and ' + str(
                self.y))
        self.pushButton_applyFilters.clicked.connect(self.clicked)

    def clicked(self):
        if self.lineEdit.text() and self.lineEdit_2.text() and self.lineEdit_3.text() \
                and self.lineEdit_4.text() and \
                self.lineEdit.text().isdigit() and self.lineEdit_2.text().isdigit() \
                and self.lineEdit_3.text().isdigit() and self.lineEdit_4.text().isdigit() and \
                0 <= int(self.lineEdit.text()) <= self.x and 0 <= int(
            self.lineEdit_2.text()) <= self.y and \
                0 <= int(self.lineEdit_3.text()) <= self.x and 0 <= int(
            self.lineEdit_4.text()) <= self.y:

            self.image = Image.fromqpixmap(self.pixmap)
            self.image = self.image.crop(
                (int(self.lineEdit.text()), int(self.lineEdit_2.text()),
                 int(self.lineEdit_3.text()), int(self.lineEdit_4.text())))

            self.x, self.y = self.image.size[0], self.image.size[1]
            self.pixmap = QPixmap.fromImage(ImageQt(self.image))

            self.image2.resize(self.x, self.y)
            self.image2.setPixmap(self.pixmap)
            self.rod_pix.setPixmap(self.pixmap)

            roi_img = self.image
            img_byte_arr = io.BytesIO()
            roi_img.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()

            self.id += 1
            self.lake.curr_image = self.image
            self.lake.currr_image = self.image

            self.rod.cursor().execute("""INSERT INTO images
                                              (image)
                                              VALUES
                                              (?)""",
                                      (img_byte_arr,)).fetchall()

            self.rod.commit()
            self.close()
        else:
            self.label_6.setText('Некорректные\nданные')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec())
