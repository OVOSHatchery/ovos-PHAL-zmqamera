from ovos_plugin_manager.templates.phal import PHALPlugin

from ovos_PHAL_zmqamera.sender import CameraSender
from ovos_utils import create_daemon

from ovos_PHAL_zmqamera.server import get_app


class PHALZMQamera(PHALPlugin):
    def __init__(self, bus, name="phal_zmqamera", config=None):
        config = config or {}
        if "host" not in config:
            raise ValueError("zmq2mjpeg server host not set in config")
        self.sender = CameraSender(config.get("host"),
                                   config.get("device_name", "my_ovos_camera"),
                                   config.get("time_between_restarts", 5),
                                   camera_index=config.get("camera_index", 0))
        super().__init__(bus, name, config or {})
        if config.get("serve_mjpeg"):
            self.server = create_daemon(self.serve_mjpeg)
        else:
            self.server = None

    def serve_mjpeg(self):
        app = get_app(self.sender)
        app.run(host="0.0.0.0")

    def run(self):
        self.sender.run()

    def shutdown(self):
        self.sender.stop()
        if self.server:
            self.server.join(0)
