import cv2

from flask import Flask, Response


def get_app(image_hub):
    app = Flask(__name__)

    def _gen_frames():  # generate frame by frame from camera
        while True:
            frame = image_hub.get()
            if frame is None:
                continue
            try:
                ret, jpeg = cv2.imencode('.jpg', frame)
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
            except Exception as e:
                pass

    @app.route('/video_feed')
    def video_feed():
        return Response(_gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

    return app


def main(conf=None):
    app = get_app(**conf)
    app.run(host="0.0.0.0")


if __name__ == "__main__":
    # TODO kwargs
    conf = {
        "name": "laptop",
        "host": "192.168.1.17"
    }
    main(conf)
