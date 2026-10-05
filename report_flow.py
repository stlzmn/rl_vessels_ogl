import time
import threading
from queue import Queue
from pyais import decode_msg
from pyais.exceptions import MissingMultipartMessageException, InvalidNMEAMessageException
from socket import socket, AF_INET, SOCK_STREAM
from entity import Vessel
from data_preparation import wgs84_to_xy

class LazySocketConn:
    def __init__(self, address, port, family=AF_INET, conn_type=SOCK_STREAM):
        self.address = address
        self.port = port
        self.family = family
        self.conn_type = conn_type
        self.local = threading.local()

    def __enter__(self):
        if hasattr(self.local, 'sock'):
            raise RuntimeError('Połączenie jest już nawiązane.')
        self.local.sock = socket(self.family, self.conn_type)
        self.local.sock.connect((self.address, self.port))
        return self.local.sock
    
    def __exit__(self, exec_ty, exec_val, tb):
        self.local.sock.close()
        del self.local.sock

class AisReportFlow:
    def __init__(self, source, destination):
        self._sentinel = object()
        self._running = True
        self._queue = Queue()
        self._set_source(source)
        self._set_destination(destination)
    
    def _set_source(self, source):
        if source == 'server':
            self.source = LazySocketConn('195.116.95.76', 3558)
        elif source == 'device':
            raise NotImplementedError()
        else:
            raise ValueError('Choose one: server | device')
        
    def _set_destination(self, destination=None):
        if destination is None:
            raise ValueError('Specify destination. Cannot be None')
        self.director = Director(destination)

    def run(self):
        t_producer = threading.Thread(target=self._producer)
        t_consumer = threading.Thread(target=self._consumer)
        t_producer.start()
        t_consumer.start()

    def terminate(self):
        self._running = False

    def _producer(self):
        with self.source as src:
            while self._running:
                line = ''
                while True:
                    char = src.recv(1).decode('utf-8')
                    if char == '\n':
                        break
                    line += char
                self._queue.put(line)
            self._queue.put(self._sentinel)

    def _consumer(self):
        while True:
            recv_report = self._queue.get()
            if recv_report is self._sentinel:
                self._queue.put(self._sentinel)
                print('AIS report flow terminated.')
                break
            self.director.decide(recv_report)

class Director:
    def __init__(self, vessel_buffer):
        self.buffer = vessel_buffer
    
    def decide(self, raw_report):
        try:
            msg = decode_msg(raw_report)
        except (MissingMultipartMessageException, InvalidNMEAMessageException) as e:
            pass
        if msg['type'] in (5,) and msg['mmsi'] in self.buffer.keys():
            self._add_static_data(msg)
        if not self.buffer:
            self._add_new_vessel(msg)
        else:
            if msg['mmsi'] in self.buffer.keys():
                self._update_old_vessel(msg)
            else:
                self._add_new_vessel(msg)

    def _add_new_vessel(self, raw_report):
        try:
            lon, lat = raw_report['lon'], raw_report['lat']
            x, y = wgs84_to_xy(lon, lat)
            vessel = Vessel(position=[x, y, 0.0], eulers=[0, 0, 0])
            self.buffer[raw_report['mmsi']] = vessel
        except KeyError:
            pass

    def _add_static_data(self, raw_report):
        pass

    def _update_old_vessel(self, raw_report):
        pass

# try:
#     msg = decode_msg(raw_report)
#     if msg['type'] in (5,) and msg['mmsi'] in Ships.get_all().keys():
#         existing_ship = Ships.get_ship_by_mmsi(msg['mmsi'])
#         existing_ship.add_static_params(msg)
#     if not len(Ships.get_all()):
#         new_ship = TargetShip(msg['mmsi'], 1., '---', '---')
#         new_ship.add_position(Position(msg['lon'], msg['lat'], msg['speed'], msg['heading'], msg['course'], msg['second']))
#         Ships.add_ship(new_ship)
#     else:
#         if msg['mmsi'] in Ships.get_all().keys():
#             existing_ship = Ships.get_ship_by_mmsi(msg['mmsi'])
#             existing_ship.add_position(Position(msg['lon'], msg['lat'], msg['speed'], msg['heading'], msg['course'], msg['second']))
#         else:
#             new_ship = TargetShip(msg['mmsi'], 1., '---', '---')
#             new_ship.add_position(Position(msg['lon'], msg['lat'], msg['speed'], msg['heading'], msg['course'], msg['second']))
#             Ships.add_ship(new_ship)
#     yield Ships.get_all()
# except (MissingMultipartMessageException, InvalidNMEAMessageException, KeyError) as e:
#     yield Ships.get_all()