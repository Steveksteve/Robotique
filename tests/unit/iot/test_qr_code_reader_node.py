from __future__ import annotations

import types

from m3pro_teacher_vision import qr_code_reader_node as qr_module
from m3pro_teacher_vision.qr_code_reader_node import QrCodeReaderNode


class FakePublisher:
    def __init__(self):
        self.messages = []

    def publish(self, msg):
        self.messages.append(msg)


def test_image_cb_publishes_detected_qr(monkeypatch):
    node = QrCodeReaderNode.__new__(QrCodeReaderNode)
    node.min_publish_interval = 0.5
    node.last_publish_at = 0.0
    node.last_qr = ""
    node.last_seen_at = 0.0
    node.qr_pub = FakePublisher()
    node.get_logger = lambda: types.SimpleNamespace(
        info=lambda *args, **kwargs: None,
        warning=lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(qr_module.np, "frombuffer", lambda data, dtype: b"frame")
    monkeypatch.setattr(qr_module.cv2, "imdecode", lambda arr, flag: "decoded-frame")
    monkeypatch.setattr(qr_module.cv2, "cvtColor", lambda frame, code: frame)
    monkeypatch.setattr(
        qr_module,
        "zbar_decode",
        lambda frame: [types.SimpleNamespace(data=b"a")],
    )

    node.image_cb(types.SimpleNamespace(data=b"raw-image"))

    assert node.last_qr == "a"
    assert node.qr_pub.messages[0].data == "a"


def test_image_cb_respects_publish_interval(monkeypatch):
    node = QrCodeReaderNode.__new__(QrCodeReaderNode)
    node.min_publish_interval = 60.0
    node.last_publish_at = 100.0
    node.last_qr = ""
    node.last_seen_at = 0.0
    node.qr_pub = FakePublisher()
    node.get_logger = lambda: types.SimpleNamespace(
        info=lambda *args, **kwargs: None,
        warning=lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(qr_module.time, "time", lambda: 120.0)
    monkeypatch.setattr(qr_module.np, "frombuffer", lambda data, dtype: b"frame")
    monkeypatch.setattr(qr_module.cv2, "imdecode", lambda arr, flag: "decoded-frame")
    monkeypatch.setattr(qr_module.cv2, "cvtColor", lambda frame, code: frame)
    monkeypatch.setattr(
        qr_module,
        "zbar_decode",
        lambda frame: [types.SimpleNamespace(data=b"a")],
    )

    node.image_cb(types.SimpleNamespace(data=b"raw-image"))

    assert node.last_qr == ""
    assert node.qr_pub.messages == []


def test_read_qr_cb_returns_last_qr_when_available():
    node = QrCodeReaderNode.__new__(QrCodeReaderNode)
    node.last_qr = "qr-123"

    response = types.SimpleNamespace(success=False, message="")
    result = node.read_qr_cb(types.SimpleNamespace(), response)

    assert result.success is True
    assert result.message == "qr-123"


def test_read_qr_cb_returns_failure_when_no_qr_seen():
    node = QrCodeReaderNode.__new__(QrCodeReaderNode)
    node.last_qr = ""

    response = types.SimpleNamespace(success=False, message="")
    result = node.read_qr_cb(types.SimpleNamespace(), response)

    assert result.success is False
    assert result.message == "No QR code detected yet"
