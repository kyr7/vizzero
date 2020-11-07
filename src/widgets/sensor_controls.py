from PySide2.QtGui import QDoubleValidator
from PySide2.QtWidgets import QGridLayout, QLabel, QCheckBox, QGroupBox, QLineEdit, QVBoxLayout

from core.core import CoreController
from sensor.sensor_wrapper import SensorSettings
from widgets.sensor_connector import SensorConnector


class SensorControls(QGroupBox):

    def __init__(self, core_controller: CoreController):
        super().__init__()
        self.amplitude_scale_input: QLineEdit = QLineEdit()
        self.sensor_controls = []
        layout = QGridLayout()
        self.sensors_group = QGroupBox()
        self.sensors_layout = QVBoxLayout()
        self.sensors_group.setLayout(self.sensors_layout)

        self.setLayout(layout)
        layout.addWidget(self.sensors_group, 0, 0, 1, 2)

        # bandpass
        bandpass_group = QGroupBox()
        bandpass_layout = QGridLayout()
        bandpass_group.setLayout(bandpass_layout)
        bandpass_label = QLabel('Bandpass')
        bandpass_checkbox = QCheckBox()

        bp_high_label = QLabel('High, Hz')
        bp_high_input = QLineEdit()
        bp_low_label = QLabel('Low, Hz')
        bp_low_input = QLineEdit()

        bandpass_layout.addWidget(bandpass_label, 0, 0)
        bandpass_layout.addWidget(bandpass_checkbox, 0, 1)
        bandpass_layout.addWidget(bp_high_label, 1, 0)
        bandpass_layout.addWidget(bp_high_input, 1, 1)
        bandpass_layout.addWidget(bp_low_label, 2, 0)
        bandpass_layout.addWidget(bp_low_input, 2, 1)
        layout.addWidget(bandpass_group, 1, 0, 1, 2)

        # notch
        notch_group = QGroupBox()
        notch_layout = QGridLayout()
        notch_group.setLayout(notch_layout)
        notch_label = QLabel('Notch')
        notch_checkbox = QCheckBox()

        notch_input_label = QLabel('Notch, Hz')
        notch_input = QLineEdit()
        notch_layout.addWidget(notch_label, 0, 0)
        notch_layout.addWidget(notch_checkbox, 0, 1)
        notch_layout.addWidget(notch_input_label, 1, 0)
        notch_layout.addWidget(notch_input, 1, 1)
        layout.addWidget(notch_group, 2, 0, 1, 2)

        # scale
        amplitude_scale_input = QLineEdit()
        amplitude_scale_input.setValidator(QDoubleValidator(0.0, 1.0, 10))
        scale_group = QGroupBox()
        scale_layout = QGridLayout()
        scale_group.setLayout(scale_layout)
        amplitude_scale_label = QLabel('Scale')
        scale_layout.addWidget(amplitude_scale_label, 2, 0)
        scale_layout.addWidget(self.amplitude_scale_input, 2, 1)

        self.bind_controls()

    def add_sensor(self, sensor_connector: SensorConnector):
        self.sensors_layout.addWidget(sensor_connector)
        self.sensor_controls.append(sensor_connector)

    def remove_sensor(self, sensor_connector: SensorConnector):
        self.sensors_layout.addWidget(sensor_connector)
        self.sensor_controls.append(sensor_connector)

    def bind_controls(self):
        self.amplitude_scale_input.textEdited.connect(self.amplitude_scale_changed)
        for sensor in self.sensor_controls:
            sensor.sensor_controller.rx_sensor_settings_subject.subscribe(self.draw_sensor_settings)

    def amplitude_scale_changed(self, amplitude_scale):
        for sensor in self.sensor_controls:
            sensor_settings: SensorSettings = sensor.sensor_controller.get_sensor_settings()
            sensor_settings.amplitude_scale = amplitude_scale
            self.sensor_controller.update_sensor_settings(sensor_settings)
