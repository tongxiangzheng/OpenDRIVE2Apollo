from xml.dom.minidom import parse
import math
import matplotlib.pyplot as plt
import os
from collections import defaultdict
import random
import itertools

mapPath="OpenDrive-maps-from-CARLA/carla_Town01.xodr"


def math_rotate(x, y, hdg):
    return math.cos(hdg) * x - math.sin(hdg) * y, math.sin(hdg) * x + math.cos(hdg) * y


class SegmentPoint:
    def __init__(self, x, y, hdg):
        self.x = x
        self.y = y
        self.hdg = hdg

    def __str__(self):
        return f'SP({self.x}, {self.y}, {self.hdg})'

    def __repr__(self):
        return str(self)


class Segment:
    def __init__(self, length):
        self.length = length

    def forward(self, start_point: SegmentPoint, left=0, length=None, reverse=False) -> SegmentPoint:
        raise NotImplementedError


class LineSegment(Segment):
    def __init__(self, length):
        super().__init__(length)

    def forward(self, start_point: SegmentPoint, left=0, length=None, reverse=False) -> SegmentPoint:
        if length is None:
            length = self.length
        if reverse:
            length = self.length - length
        start_point = SegmentPoint(
            start_point.x + math.cos(start_point.hdg + math.pi / 2) * left,
            start_point.y + math.sin(start_point.hdg + math.pi / 2) * left,
            start_point.hdg
        )
        return SegmentPoint(start_point.x + math.cos(start_point.hdg) * length,
                            start_point.y + math.sin(start_point.hdg) * length,
                            start_point.hdg)

    def __str__(self):
        return f'Line({self.length})'

    def __repr__(self):
        return str(self)


class ArcSegment(Segment):
    def __init__(self, length, curvature):
        super().__init__(length)
        self.curvature = curvature

    def forward(self, start_point: SegmentPoint, left=0, length=None, reverse=False) -> SegmentPoint:
        if length is None:
            length = self.length
        if reverse:
            length = self.length - length
        start_point = SegmentPoint(
            start_point.x + math.cos(start_point.hdg + math.pi / 2) * left,
            start_point.y + math.sin(start_point.hdg + math.pi / 2) * left,
            start_point.hdg
        )
        cr = 1 / self.curvature
        nr = cr - left
        length = length / cr * nr
        curvature = 1 / nr
        dx = math.cos(length * curvature - math.pi / 2) / curvature
        dy = 1 / curvature + math.sin(length * curvature - math.pi / 2) / curvature
        dx, dy = math_rotate(dx, dy, start_point.hdg)
        x = start_point.x + dx
        y = start_point.y + dy
        return SegmentPoint(x, y, start_point.hdg + length * curvature)

    def __str__(self):
        return f'Arc({self.length}, {self.curvature})'

    def __repr__(self):
        return str(self)

SIGNAL_STOP_SIGN = 'st'
SIGNAL_YIELD_SIGN = 'yd'
SIGNAL_TRAFFIC_LIGHT = 'lt'


class Signal:
    def __init__(self, _type, s):
        self.type = _type
        self.s = s


class Lane:
    def __init__(self, name, start_points, segments, lateral_offset, is_junction: bool, reverse: bool, signals):
        self.name = name
        self.start_points = start_points
        self.lateral_offset = lateral_offset
        self.segments = segments
        self.is_junction = is_junction
        self.reverse = reverse
        self.length = sum([seg.length for seg in self.segments])
        self.signals = []
        for signal in signals:
            self.signals.append(Signal(signal.type, self.length - signal.s))
        assert len(self.start_points) == len(self.segments), f'{len(self.start_points)} != {len(self.segments)}'

    def forward(self, length=None):
        if length is None:
            length = self.length
        if self.reverse:
            length = self.length - length
        if length <= 0:
            length = 0
        if length >= self.length:
            length = self.length
        for start_point, segment in zip(self.start_points, self.segments):
            if length >= segment.length:
                length -= segment.length
            else:
                return segment.forward(start_point, self.lateral_offset, length)
        return self.segments[-1].forward(self.start_points[-1], self.lateral_offset)


class OpenDriveMap:
    def __init__(self, name: str):
        self.doc = parse(mapPath)

    def lanes(self):
        ret = []
        id_signal_map = dict()
        signal_nodes = self.doc.getElementsByTagName('signal')
        for signal_node in signal_nodes:
            signal_id = signal_node.getAttribute('id')
            signal_name = signal_node.getAttribute('name')
            signal_s = float(signal_node.getAttribute('s'))
            for validity_node in signal_node.getElementsByTagName('validity'):
                from_lane, to_lane = int(validity_node.getAttribute('fromLane')), \
                    int(validity_node.getAttribute('toLane'))
                # assert from_lane == to_lane == 0, f"{from_lane}, {to_lane}"
            signal_type = 'unknown'
            if 'Stop' in signal_name:
                signal_type = SIGNAL_STOP_SIGN
            if 'Yield' in signal_name:
                signal_type = SIGNAL_YIELD_SIGN
            if 'Light' in signal_name:
                signal_type = SIGNAL_TRAFFIC_LIGHT
            id_signal_map[signal_id] = Signal(signal_type, signal_s)

        for road_node in self.doc.getElementsByTagName('road'):
            lane_signals = defaultdict(list)
            signal_reference_nodes = road_node.getElementsByTagName('signalReference')
            signal_nodes = road_node.getElementsByTagName('signal')
            for signal_reference_node in itertools.chain(signal_reference_nodes, signal_nodes):
                rid = signal_reference_node.getAttribute('id')
                if rid in id_signal_map:
                    for validity_node in signal_reference_node.getElementsByTagName('validity'):
                        from_lane, to_lane = int(validity_node.getAttribute('fromLane')), \
                            int(validity_node.getAttribute('toLane'))
                        for i in range(int(from_lane), int(to_lane) + 1):
                            lane_signals[i].append(id_signal_map[rid])

            road_name = road_node.getAttribute('name')
            start_points = []
            segments = []
            is_junction = (road_node.getAttribute('junction') != "-1")
            segment_nodes = road_node.getElementsByTagName('planView')[0].getElementsByTagName('geometry')
            for segment_node in segment_nodes:
                start_points.append(SegmentPoint(float(segment_node.getAttribute('x')),
                                                 float(segment_node.getAttribute('y')),
                                                 float(segment_node.getAttribute('hdg'))))
                if len(segment_node.getElementsByTagName('line')) > 0:
                    segments.append(LineSegment(float(segment_node.getAttribute('length'))))
                elif len(segment_node.getElementsByTagName('arc')) > 0:
                    arc_node = segment_node.getElementsByTagName('arc')[0]
                    curvature = float(arc_node.getAttribute('curvature'))
                    length = float(segment_node.getAttribute('length'))
                    segments.append(ArcSegment(length, curvature))
                else:
                    raise ValueError
            start_points, segments = tuple(start_points), tuple(segments)
            for d in ['left', 'right']:
                width_offset = 0
                offset_nodes = road_node.getElementsByTagName('laneOffset')
                if len(offset_nodes) > 0:
                    if d == 'left':
                        width_offset += float(offset_nodes[len(offset_nodes) // 2].getAttribute('a'))
                    else:
                        width_offset -= float(offset_nodes[len(offset_nodes) // 2].getAttribute('a'))
                nodes = road_node.getElementsByTagName(d)
                if len(nodes) > 0:
                    node = nodes[0]
                    lane_nodes = node.getElementsByTagName('lane')
                    id_lane_map = {
                        int(lane.getAttribute("id")): lane for lane in lane_nodes
                    }
                    for lid in sorted(id_lane_map.keys(), key=lambda x: abs(x)):
                        lane_node = id_lane_map[lid]
                        lane_width = abs(float(lane_node.getElementsByTagName('width')[0].getAttribute('a')))
                        offset = width_offset + lane_width / 2
                        if lane_node.getAttribute('type') in ['driving', 'bidirectional'] or True:
                        # if lane_node.getAttribute('type') not in ['sidewalk', 'shoulder']:
                            ret.append(
                                Lane(f'{road_name}({lid})', start_points, segments, (offset if d == 'left' else -offset),
                                     is_junction, d == 'left', lane_signals[lid]))
                        width_offset += lane_width
        return ret

class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def magnitude(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def __add__(self, other: 'Vector'):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other: 'Vector'):
        return Vector(self.x - other.x, self.y - other.y)

    def __rmul__(self, k):
        return Vector(self.x * k, self.y * k)

class Ploter:
    def plot_lane(self, lane: Lane):
        if lane.length < 0.1:
            return
        xs = []
        ys = []
        ts = []
        t = 0
        while t < lane.length:
            p = lane.forward(t)
            xs.append(p.x)
            ys.append(p.y)
            ts.append(t)
            t += 0.05
        p = lane.forward()
        xs.append(p.x)
        ys.append(p.y)
        ts.append(lane.length)
        # print(list((x, y, t) for x, y, t in zip(xs, ys, ts)))
        plt.plot(xs, ys, c='green' if lane.is_junction else 'blue')

        head_length = 2
        source = Vector(xs[-3], ys[-3])
        target = Vector(xs[-1], ys[-1])
        vec = target - source
        source = source - (head_length / vec.magnitude()) * vec
        mid_index = len(xs) // 2
        plt.text(xs[mid_index], ys[mid_index], lane.name)
        color_map = {
            SIGNAL_YIELD_SIGN: 'yellow',
            SIGNAL_STOP_SIGN: 'red',
            SIGNAL_TRAFFIC_LIGHT: 'green',
            'unknown': 'pink',
        }
        for signal in lane.signals:
            p = lane.forward(signal.s)
            plt.scatter([p.x], [p.y], c=color_map[signal.type])
            plt.text(p.x + random.random(), p.y + random.random(), signal.type + f' (for {lane.name})')

        plt.arrow(source.x, source.y, vec.x, vec.y, head_width=1, head_length=head_length)

    def plot_segment(self, start_point: SegmentPoint, segment: Segment):
        xs = []
        ys = []
        t = 0
        while t < segment.length:
            p = segment.forward(start_point, 0, t)
            xs.append(p.x)
            ys.append(p.y)
            t += 0.1
        plt.plot(xs, ys, c='red')

mp = OpenDriveMap('Town01')
lanes = mp.lanes()
ploter = Ploter()
for lane in lanes:
    ploter.plot_lane(lane)
    # for p, s in zip(lane.start_points, lane.segments):
        # print(p, s)
        # if not lane.is_junction:
        #     plt.scatter([p.x], [p.y], c='green')
        # ploter.plot_segment(p, s)
plt.axis('equal')
plt.show()
