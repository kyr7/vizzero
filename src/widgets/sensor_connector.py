from PySide2.QtWidgets import QGridLayout, QLabel, QCheckBox, QGroupBox, QLineEdit, QComboBox

from core.core import SensorController
from sensor.sensor_wrapper import SensorSettings


class SensorConnector(QGroupBox):

    sensor_controller: SensorController = None
    simulate_checkbox: QCheckBox = None
    sensor_port_input: QComboBox = None

    def __init__(self, sensor_controller: SensorController):
        super().__init__()
        self.sensor_controller = sensor_controller
        layout = QGridLayout()
        self.setLayout(layout)
        self.setMaximumHeight(400)

        # simulate
        select_sensor_group = QGroupBox()
        controls_layout = QGridLayout()
        select_sensor_group.setLayout(controls_layout)
        simulate_label = QLabel('Simulate')
        self.simulate_checkbox = QCheckBox()
        sensor_port_label = QLabel('Sensor COM')
        self.sensor_port_input = QComboBox()
        self.sensor_port_input.setEditable(True)

        controls_layout.addWidget(simulate_label, 0, 0)
        controls_layout.addWidget(self.simulate_checkbox, 0, 1)
        controls_layout.addWidget(sensor_port_label, 1, 0)
        controls_layout.addWidget(self.sensor_port_input, 1, 1)

        layout.addWidget(select_sensor_group, 0, 0, 1, 2)

    def update_sensor_settings(self, simulate=None, com_port=None, amplitude_scale=None):
        sensor_settings: SensorSettings = self.sensor_controller.get_sensor_settings()
        if simulate is not None:
            sensor_settings.simulation = simulate
        if com_port is not None:
            sensor_settings.sensor_com_port = com_port
        if amplitude_scale is not None:
            sensor_settings.amplitude_scale = amplitude_scale
        self.sensor_controller.update_sensor_settings(sensor_settings)

    def simulate_clicked(self, checked):
        self.update_sensor_settings(simulate=checked)

    def com_port_changed(self, com_port):
        self.update_sensor_settings(com_port=com_port)

    def update_com_items(self):
        com_ports = self.sensor_controller.list_serial_ports()
        while self.sensor_port_input.count() > 0:
            self.sensor_port_input.removeItem(0)
        for com_port in com_ports:
            self.sensor_port_input.addItem(com_port)

    def bind_controls(self):
        self.update_com_items()
        self.simulate_checkbox.stateChanged.connect(self.simulate_clicked)
        self.sensor_port_input.currentIndexChanged.connect(self.com_port_changed)
        # self.sensor_port_input.activated.connect(self.update_com_items)
        self.amplitude_scale_input.textEdited.connect(self.amplitude_scale_changed)

    def draw_sensor_settings(self, sensor_settings: SensorSettings):
        self.simulate_checkbox.setChecked(sensor_settings.simulation)
        amplitude_text_position = self.amplitude_scale_input.cursorPosition()
        self.amplitude_scale_input.setText(sensor_settings.amplitude_scale.__str__())
        self.amplitude_scale_input.setCursorPosition(min(amplitude_text_position, self.amplitude_scale_input.cursorPosition()))

