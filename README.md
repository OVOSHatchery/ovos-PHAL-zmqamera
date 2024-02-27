# PHAL ZMQamera

Expose your OVOS device camera via [imagezmq](https://github.com/jeffbass/imagezmq) for remote processing

> This plugin needs a imagezmq server running, it is suitable for when you need to read the camera in a remote device

## Home Assistant

You can use the `"serve_mjpeg"` option to integrate this camera [into Home Assistant](https://www.home-assistant.io/integrations/mjpeg/)

![img.png](img.png)

## Configuration

```javascript
{
  "PHAL": {
    "ovos-PHAL-zmqamera": {
      "host": "tcp://0.0.0.0:5555",
      "device_name": "my_phal_device",
      "camera_index": 0,
      "serve_mjpeg": false, // serve a mjpeg camera stream at http://0.0.0.0:5000/video_feed
      "time_between_restarts": 5
    }
  }
}
```

## Consuming the feed

```python
from threading import Thread

import imagezmq
import simplejpeg


class CamReader(Thread):
    cameras = {}

    def __init__(self, daemon=True):
        super().__init__(daemon=daemon)
        self.image_hub = imagezmq.ImageHub()

    def run(self):
        while True:

            rpi_name, jpg_buffer = self.image_hub.recv_jpg()
            frame = simplejpeg.decode_jpeg(jpg_buffer, colorspace='BGR')
            self.image_hub.send_reply(b'OK')
            
            # do stuff

    def get(self, name):
        cam = CamReader.cameras.get(name)
        if cam:
            return cam.last_frame

```