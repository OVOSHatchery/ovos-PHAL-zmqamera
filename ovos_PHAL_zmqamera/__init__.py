from ovos_plugin_manager.templates.phal import PHALPlugin

from ovos_PHAL_zmqamera.sender import CameraSender


class PHALZMQamera(PHALPlugin):
    def __init__(self, bus, name="phal_zmqamera", config=None):
        config = config or {}
        if "host" not in config:
            raise ValueError("zmq2mjpeg server host not set in config")
        self.sender = CameraSender(config.get("host"),
                                   config.get("device_name", "my_ovos_camera"),
                                   config.get("time_between_restarts", 5))
        super().__init__(bus, name, config or {})

    def run(self):
        self.sender.run()

    def shutdown(self):
        self.sender.stop()
