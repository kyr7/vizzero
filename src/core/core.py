import sys
import traceback

from rx import zip, operators as op

sys.path.append('file')
sys.path.append('sensor')
from sensor.sensor_wrapper import *
import serial.tools.list_ports
from file.fileUtil import *
from PySide2.QtWidgets import QPushButton
import threading
from rx.subject import Subject, BehaviorSubject


class FileController:
    file_writer = None

    def start_file(self, dir, name):
        self.file_writer = FileWriter(dir, name.name)
        self.file_writer.start_file()

    def append_data(self, data):
        self.file_writer.append_data(data)

    def finish_file(self):
        if self.file_writer is not None:
            self.file_writer.finish_file()
            self.file_writer = None

    def delete_latest_file(self):
        self.file_writer.delete_latest_file()


class DataThread(threading.Thread):
    sensor = None
    data_running = True
    rx_sensor_data_subject = None
    rx_sensor_settings_subject = None

    def __init__(self, rx_sensor_data_subject, rx_sensor_settings_subject):
        super(DataThread, self).__init__()
        self.sensor = None
        self.rx_sensor_data_subject = rx_sensor_data_subject
        self.rx_sensor_settings_subject = rx_sensor_settings_subject

    def stop(self):
        self.data_running = False

    def run(self):
        try:
            self.sensor = SensorWrapper(self.rx_sensor_settings_subject)
            while self.data_running:
                data = self.sensor.read_filtered()
                if data is not None:
                    self.rx_sensor_data_subject.on_next(data)
                sleep(0.01)
        except Exception:
            traceback.print_exc(file=sys.stdout)
            self.stop()
        finally:
            self.sensor.disconnect()


class SensorController:
    rx_sensor_data_subject = None
    rx_sensor_settings_subject = None
    data_thread = None

    def __init__(self, sensor_settings: SensorSettings = SensorSettings()):
        self.rx_sensor_data_subject = Subject()
        self.rx_sensor_settings_subject = BehaviorSubject(sensor_settings)

    def start_data(self):
        if self.data_thread is None or not self.data_thread.data_running:
            self.data_thread = DataThread(self.rx_sensor_data_subject, self.rx_sensor_settings_subject)
            self.data_thread.start()

    def stop_data(self):
        if self.data_thread is not None:
            self.data_thread.stop()
            self.data_thread = None

    def sensor_connected(self):
        return self.data_thread is not None

    def update_sensor_settings(self, sensor_settings: SensorSettings):
        self.rx_sensor_settings_subject.on_next(sensor_settings)

    def get_sensor_settings(self):
        return self.rx_sensor_settings_subject.value

    def list_serial_ports(self):
        return [comport.device for comport in serial.tools.list_ports.comports()]


class CoreController:
    file_controller = None
    file_sensor_subs = None
    sensor_controllers = []
    multisensor_data_subject: Subject = Subject()

    def __init__(self):
        self.file_controller = FileController()

        sensor_settings1 = SensorSettings()
        # sensor_settings1.other_info = '1'
        sensor_settings1.sensor_com_port = "/dev/ttyACM2"
        self.sensor_controllers.append(SensorController(sensor_settings1))

        sensor_settings2 = SensorSettings()
        # sensor_settings2.other_info = '2'
        sensor_settings2.sensor_com_port = "/dev/ttyACM3"
        self.sensor_controllers.append(SensorController(sensor_settings2))

    def _concat_sensors(self, sens_data):
        sensors_data_list = [*sens_data]
        min_length = min(map(lambda x: x.shape[0], [*sens_data]))
        trimmed = list(map(lambda x: x[:min_length], sensors_data_list))
        return np.concatenate(trimmed, axis=1)

    def start_data(self):
        rx_sensor_subjects = []
        for sensor_controller in self.sensor_controllers:
            sensor_controller.start_data()
            rx_sensor_subjects.append(sensor_controller.rx_sensor_data_subject)
        sensor_subject = zip(
            self.sensor_controllers[0].rx_sensor_data_subject,
            self.sensor_controllers[1].rx_sensor_data_subject).pipe(
            op.map(self._concat_sensors)
        )
        # sensor_subject = self.sensor_controllers[0].rx_sensor_data_subject
        sensor_subject.subscribe(self.multisensor_data_subject)

    def stop_data(self):
        for sensor_controller in self.sensor_controllers:
            sensor_controller.stop_data()

    def write_to_file(self, dir, file_name):
        if self.file_sensor_subs is None:
            self.file_controller.start_file(dir, file_name)
            self.file_sensor_subs = self.multisensor_data_subject.subscribe(
                self.file_controller.append_data)

    def finish_file(self):
        if self.file_sensor_subs is not None:
            self.file_sensor_subs.dispose()
            self.file_sensor_subs = None
            self.file_controller.finish_file()


class BasePlugin:
    core_controller = None

    def __init__(self, core_controller=None):
        self.core_controller = core_controller

    def create_widget(self, parent=None):
        return QPushButton('Dummy widget')

    def destroy(self):
        pass

    def get_name(self):
        return ""
