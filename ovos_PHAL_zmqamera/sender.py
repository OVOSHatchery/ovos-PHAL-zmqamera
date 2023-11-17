from time import sleep

import imagezmq
import simplejpeg
import zmq  # needed because we will be using zmq socket options & exceptions
from imutils.video import VideoStream


class CameraSender:
    def __init__(self, host, name, time_between_restarts=5, jpeg_quality=95):
        self.running = False
        self.host = host
        self.name = name  # some unique device name here
        self.time_between_restarts = time_between_restarts  # number of seconds to sleep between sender restarts
        self.jpeg_quality = jpeg_quality  # 0 to 100, higher is better quality

    @staticmethod
    def sender_start(connect_to=None):
        sender = imagezmq.ImageSender(connect_to=connect_to)
        sender.zmq_socket.setsockopt(zmq.LINGER, 0)  # prevents ZMQ hang on exit
        # NOTE: because of the way PyZMQ and imageZMQ are implemented, the
        #       timeout values specified must be integer constants, not variables.
        #       The timeout value is in milliseconds, e.g., 2000 = 2 seconds.
        sender.zmq_socket.setsockopt(zmq.RCVTIMEO, 2000)  # set a receive timeout
        sender.zmq_socket.setsockopt(zmq.SNDTIMEO, 2000)  # set a send timeout
        return sender

    def stop(self):
        self.running = False

    def run(self):
        sender = self.sender_start(self.host)

        picam = VideoStream().start()

        self.running = True
        try:
            while self.running:  # send images as stream until Ctrl-C
                image = picam.read()
                jpg_buffer = simplejpeg.encode_jpeg(image, quality=self.jpeg_quality,
                                                    colorspace='BGR')
                try:
                    reply_from_mac = sender.send_jpg(self.name, jpg_buffer)
                except (zmq.ZMQError, zmq.ContextTerminated, zmq.Again):
                    if 'sender' in locals():
                        print('Closing ImageSender.')
                        sender.close()
                    sleep(self.time_between_restarts)
                    print('Restarting ImageSender.')
                    sender = self.sender_start(self.host)
        except (KeyboardInterrupt, SystemExit):
            self.running = False  # Ctrl-C was pressed to end program
        except Exception as ex:
            print('Python error with no Exception handler:')
            print('Traceback error:', ex)
        finally:
            if 'sender' in locals():
                sender.close()
            picam.stop()  # stop the camera thread
