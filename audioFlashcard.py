import sys
import random

from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtWidgets import (
    QWidget,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QMainWindow,
    QLabel,
    QLineEdit,
    QApplication,
    QTabWidget,
    QSpinBox,
    QSpacerItem,
    QSizePolicy,
)

from audioLibrary import AudioLibrary


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Latino Numbers (0-1000)")
        self.resize(200, 150)

        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        self.tab2 = SettingsPanel()
        self.tab1 = MainPanel(self.tab2)

        self.tab_widget.addTab(self.tab1, "Main")
        self.tab_widget.addTab(self.tab2, "Settings")


class SettingsPanel(QWidget):
    def __init__(self):
        super().__init__()

        self.min_val = 0
        self.max_val = 1000

        self.label = QLabel("Settings:")

        # what range of numbers do you want to guess?
        # 0 - 99
        # 0 - 200
        # 0 - 500
        # 500 - 999
        self.label_slider = QLabel("Range of values:")
        # self.slider = QRangeSlider(Qt.Orientation.Horizontal) # Create a horizontal slider
        # self.slider.setRange(0,1000)
        # self.slider.setValue((self.min_val,self.max_val))

        self.min_spinbox = QSpinBox()
        self.min_spinbox.setValue(0)
        self.min_spinbox.setMinimum(0)

        self.max_spinbox = QSpinBox()
        self.max_spinbox.setMaximum(1000)
        self.max_spinbox.setValue(1000)

        def spin_handler():
            _min = self.min_spinbox.value()
            _max = self.max_spinbox.value()

            self.min_spinbox.setMaximum(_max - 1)
            self.max_spinbox.setMinimum(_min + 1)

        self.min_spinbox.valueChanged.connect(spin_handler)
        self.max_spinbox.valueChanged.connect(spin_handler)

        # self.min_max_label=QLabel()
        # self.min_max_label.setText("(%s,%s)" % (self.min_val, self.max_val))

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.label_slider)

        hlayout = QHBoxLayout()
        hlayout.addWidget(QLabel("Min:"))
        hlayout.addWidget(self.min_spinbox)
        hlayout.addSpacerItem(
            QSpacerItem(
                150, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
            )
        )
        layout.addLayout(hlayout)

        hlayout1 = QHBoxLayout()
        hlayout1.addWidget(QLabel("Max:"))
        hlayout1.addWidget(self.max_spinbox)
        hlayout1.addSpacerItem(
            QSpacerItem(
                150, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
            )
        )
        layout.addLayout(hlayout1)

        self.setLayout(layout)

    def get_settings(self):
        return self.min_spinbox.value(), self.max_spinbox.value()


class MainPanel(QWidget):
    def __init__(self, settingsPanel):
        super().__init__()

        self.number = "1"
        self.library = AudioLibrary()

        self.settingsPanel = settingsPanel

        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.reset()
        self.audio_output.setVolume(50)

        self.play_button = QPushButton("Play")
        self.ans_button = QPushButton("Answer")

        self.label = QLabel("Make a Guess..")
        font = self.label.font()
        font.setPointSize(12)
        self.label.setFont(font)

        self.text_input = QLineEdit()
        self.text_input.setMaxLength(3)
        self.text_input.returnPressed.connect(self.returnPressed)

        layout = QVBoxLayout()
        hlayout = QHBoxLayout()
        hlayout.addWidget(self.play_button)
        hlayout.addWidget(self.ans_button)
        layout.addLayout(hlayout)
        layout.addWidget(self.label)
        hlayout1 = QHBoxLayout()
        hlayout1.addWidget(self.text_input)
        hlayout1.addSpacerItem(
            QSpacerItem(
                150, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
            )
        )
        layout.addLayout(hlayout1)
        self.setLayout(layout)

        self.play_button.clicked.connect(self.play_once)
        self.ans_button.clicked.connect(self.display_answer)
        self.play_once()

    def reset(self):
        _min, _max = self.settingsPanel.get_settings()
        self.number = str(random.randint(_min, _max))

        _sound = self.library.get(self.number)
        self.player.setSourceDevice(_sound)

    def play_once(self):
        # print("play once")
        self.player.play()
        self.text_input.setFocus()

    def display_answer(self):
        self.label.setText(self.number)
        self.reset()
        self.play_once()

    def returnPressed(self):
        _text = self.text_input.text()
        self.text_input.clear()

        if _text == self.number:
            self.reset()
            self.label.setText("%s is correct" % _text)
            self.play_once()
        elif _text == "":
            self.play_once()
            # print(self.number)
        else:  # must have guessed the wrong number.
            # output incorrect
            self.label.setText("%s is incorrect, try again" % _text)
            self.play_once()


if __name__ == "__main__":
    app = QApplication([])
    win = MainWindow()
    win.show()
    win.tab1.text_input.setFocus()  # must have this to have cursor be on QEditLine widget
    sys.exit(app.exec())
