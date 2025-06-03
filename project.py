import sys
import os
import vlc
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout,
    QSlider, QFileDialog, QLabel
)
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtCore import Qt, QTimer


class VideoPlayer(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PyQt5 + VLC Media Player")
        self.setGeometry(300, 100, 900, 600)
        self.is_fullscreen = False
        self.playlist = []
        self.current_index = 0

        self.init_ui()
        self.show()

    def init_ui(self):
        vlc_path = r"C:\Program Files\VideoLAN\VLC"
        os.add_dll_directory(vlc_path)
        self.instance = vlc.Instance('--no-video-title-show', '--avcodec-hw=none')
        self.mediaPlayer = self.instance.media_player_new()

        self.videoFrame = QWidget(self)
        self.videoFrame.setStyleSheet("background-color: black;")
        self.videoFrame.mouseDoubleClickEvent = self.toggle_fullscreen

        openBtn = QPushButton('Open')
        openBtn.setStyleSheet(self.button_style())
        openBtn.clicked.connect(self.open_file)

        self.playBtn = QPushButton('Play')
        self.playBtn.setStyleSheet(self.button_style())
        self.playBtn.setEnabled(False)
        self.playBtn.clicked.connect(self.play_video)

        self.pauseBtn = QPushButton('Pause')
        self.pauseBtn.setStyleSheet(self.button_style())
        self.pauseBtn.setEnabled(False)
        self.pauseBtn.clicked.connect(self.pause_video)

        self.stopBtn = QPushButton('Stop')
        self.stopBtn.setStyleSheet(self.button_style())
        self.stopBtn.setEnabled(False)
        self.stopBtn.clicked.connect(self.stop_video)


        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 1000)
        self.positionSlider.setStyleSheet(self.slider_style())
        self.positionSlider.sliderMoved.connect(self.set_position)

        self.volumeSlider = QSlider(Qt.Horizontal)
        self.volumeSlider.setValue(100)
        self.volumeSlider.setMaximum(100)
        self.volumeSlider.setFixedWidth(100)
        self.volumeSlider.setStyleSheet(self.slider_style())
        self.volumeSlider.valueChanged.connect(self.set_volume)


        self.timeLabel = QLabel("00:00 / 00:00")
        self.timeLabel.setStyleSheet("color: #333; padding: 0 6px;")


        self.timer = QTimer(self)
        self.timer.setInterval(500)
        self.timer.timeout.connect(self.update_ui)


        controls = QHBoxLayout()
        controls.setSpacing(10)
        controls.addWidget(openBtn)
        controls.addWidget(self.playBtn)
        controls.addWidget(self.pauseBtn)
        controls.addWidget(self.stopBtn)
        controls.addWidget(self.positionSlider)
        controls.addWidget(self.timeLabel)
        controls.addWidget(self.volumeSlider)


        layout = QVBoxLayout()
        layout.setContentsMargins(6, 6, 6, 6)
        layout.addWidget(self.videoFrame, stretch=1)
        layout.addLayout(controls)
        self.setLayout(layout)

    def button_style(self):
        return (
            "QPushButton { background-color: #f0f0f0; border: 1px solid #707070; "
            "border-radius: 5px; padding: 6px 10px; }"
            "QPushButton:hover { background-color: #e0e0e0; }"
        )

    def slider_style(self):
        return (
            "QSlider::groove:horizontal { height: 6px; background: #f0f0f0; "
            "border: 1px solid #707070; border-radius: 3px; }"
            "QSlider::handle:horizontal { background: #007bff; border: 1px solid #0056b3; "
            "width: 14px; margin: -5px 0px; border-radius: 7px; }"
            "QSlider::add-page:horizontal { background: white; }"
            "QSlider::sub-page:horizontal { background: #007bff; }"
        )

    def open_file(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Open Videos")
        if files:
            self.playlist = files
            self.current_index = 0
            self.load_media(self.playlist[self.current_index])

    def load_media(self, path):
        self.media = self.instance.media_new(path)
        self.mediaPlayer.set_media(self.media)

        if sys.platform == "win32":
            self.mediaPlayer.set_hwnd(self.videoFrame.winId())
        else:
            self.mediaPlayer.set_xwindow(self.videoFrame.winId())

        self.playBtn.setEnabled(True)
        self.pauseBtn.setEnabled(True)
        self.stopBtn.setEnabled(True)
        self.play_video()

    def play_video(self):
        self.mediaPlayer.play()
        self.timer.start()

    def pause_video(self):
        self.mediaPlayer.pause()

    def stop_video(self):
        self.mediaPlayer.stop()
        self.timer.stop()
        self.positionSlider.setValue(0)
        self.timeLabel.setText("00:00 / 00:00")

    def set_volume(self, volume):
        self.mediaPlayer.audio_set_volume(volume)

    def set_position(self, position):
        self.mediaPlayer.set_position(position / 1000.0)

    def update_ui(self):
        if self.mediaPlayer.is_playing():
            pos = self.mediaPlayer.get_position()
            length = self.mediaPlayer.get_length()
            current = self.mediaPlayer.get_time()

            if length > 0:
                self.positionSlider.blockSignals(True)
                self.positionSlider.setValue(int(pos * 1000))
                self.positionSlider.blockSignals(False)
                self.timeLabel.setText(f"{self.format_time(current)} / {self.format_time(length)}")

            # Переключение на следующее видео
            if pos >= 0.99:
                self.timer.stop()
                self.next_video()

    def next_video(self):
        if self.current_index + 1 < len(self.playlist):
            self.current_index += 1
            self.load_media(self.playlist[self.current_index])

    def toggle_fullscreen(self, event):
        if self.is_fullscreen:
            self.showNormal()
        else:
            self.showFullScreen()
        self.is_fullscreen = not self.is_fullscreen

    def format_time(self, ms):
        if ms <= 0:
            return "00:00"
        seconds = ms // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{int(minutes):02}:{int(seconds):02}"

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        if key == Qt.Key_Space:
            self.pause_video() if self.mediaPlayer.is_playing() else self.play_video()
        elif key == Qt.Key_Right:
            self.mediaPlayer.set_time(self.mediaPlayer.get_time() + 10000)
        elif key == Qt.Key_Left:
            self.mediaPlayer.set_time(self.mediaPlayer.get_time() - 10000)
        elif key == Qt.Key_Up:
            vol = self.mediaPlayer.audio_get_volume()
            self.mediaPlayer.audio_set_volume(min(100, vol + 10))
        elif key == Qt.Key_Down:
            vol = self.mediaPlayer.audio_get_volume()
            self.mediaPlayer.audio_set_volume(max(0, vol - 10))
        elif key == Qt.Key_Plus or key == Qt.Key_Equal:
            rate = self.mediaPlayer.get_rate()
            self.mediaPlayer.set_rate(rate + 0.25)
        elif key == Qt.Key_Minus:
            rate = self.mediaPlayer.get_rate()
            self.mediaPlayer.set_rate(max(0.25, rate - 0.25))
        elif key == Qt.Key_0:
            self.mediaPlayer.set_rate(1.0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = VideoPlayer()
    sys.exit(app.exec_())
