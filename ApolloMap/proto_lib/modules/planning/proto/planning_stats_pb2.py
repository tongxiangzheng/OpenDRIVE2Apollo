# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: modules/planning/proto/planning_stats.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='modules/planning/proto/planning_stats.proto',
  package='apollo.planning',
  syntax='proto2',
  serialized_options=None,
  serialized_pb=_b('\n+modules/planning/proto/planning_stats.proto\x12\x0f\x61pollo.planning\"Z\n\nStatsGroup\x12\x0b\n\x03max\x18\x01 \x01(\x01\x12\x18\n\x03min\x18\x02 \x01(\x01:\x0b\x31\x30\x30\x30\x30\x30\x30\x30\x30\x30\x30\x12\x0b\n\x03sum\x18\x03 \x01(\x01\x12\x0b\n\x03\x61vg\x18\x04 \x01(\x01\x12\x0b\n\x03num\x18\x05 \x01(\x05\"\xa6\x02\n\rPlanningStats\x12\x36\n\x11total_path_length\x18\x01 \x01(\x0b\x32\x1b.apollo.planning.StatsGroup\x12\x34\n\x0ftotal_path_time\x18\x02 \x01(\x0b\x32\x1b.apollo.planning.StatsGroup\x12&\n\x01v\x18\x03 \x01(\x0b\x32\x1b.apollo.planning.StatsGroup\x12&\n\x01\x61\x18\x04 \x01(\x0b\x32\x1b.apollo.planning.StatsGroup\x12*\n\x05kappa\x18\x05 \x01(\x0b\x32\x1b.apollo.planning.StatsGroup\x12+\n\x06\x64kappa\x18\x06 \x01(\x0b\x32\x1b.apollo.planning.StatsGroup')
)




_STATSGROUP = _descriptor.Descriptor(
  name='StatsGroup',
  full_name='apollo.planning.StatsGroup',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='max', full_name='apollo.planning.StatsGroup.max', index=0,
      number=1, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='min', full_name='apollo.planning.StatsGroup.min', index=1,
      number=2, type=1, cpp_type=5, label=1,
      has_default_value=True, default_value=float(10000000000),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='sum', full_name='apollo.planning.StatsGroup.sum', index=2,
      number=3, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='avg', full_name='apollo.planning.StatsGroup.avg', index=3,
      number=4, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='num', full_name='apollo.planning.StatsGroup.num', index=4,
      number=5, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=64,
  serialized_end=154,
)


_PLANNINGSTATS = _descriptor.Descriptor(
  name='PlanningStats',
  full_name='apollo.planning.PlanningStats',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='total_path_length', full_name='apollo.planning.PlanningStats.total_path_length', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='total_path_time', full_name='apollo.planning.PlanningStats.total_path_time', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='v', full_name='apollo.planning.PlanningStats.v', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='a', full_name='apollo.planning.PlanningStats.a', index=3,
      number=4, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='kappa', full_name='apollo.planning.PlanningStats.kappa', index=4,
      number=5, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='dkappa', full_name='apollo.planning.PlanningStats.dkappa', index=5,
      number=6, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=157,
  serialized_end=451,
)

_PLANNINGSTATS.fields_by_name['total_path_length'].message_type = _STATSGROUP
_PLANNINGSTATS.fields_by_name['total_path_time'].message_type = _STATSGROUP
_PLANNINGSTATS.fields_by_name['v'].message_type = _STATSGROUP
_PLANNINGSTATS.fields_by_name['a'].message_type = _STATSGROUP
_PLANNINGSTATS.fields_by_name['kappa'].message_type = _STATSGROUP
_PLANNINGSTATS.fields_by_name['dkappa'].message_type = _STATSGROUP
DESCRIPTOR.message_types_by_name['StatsGroup'] = _STATSGROUP
DESCRIPTOR.message_types_by_name['PlanningStats'] = _PLANNINGSTATS
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

StatsGroup = _reflection.GeneratedProtocolMessageType('StatsGroup', (_message.Message,), dict(
  DESCRIPTOR = _STATSGROUP,
  __module__ = 'modules.planning.proto.planning_stats_pb2'
  # @@protoc_insertion_point(class_scope:apollo.planning.StatsGroup)
  ))
_sym_db.RegisterMessage(StatsGroup)

PlanningStats = _reflection.GeneratedProtocolMessageType('PlanningStats', (_message.Message,), dict(
  DESCRIPTOR = _PLANNINGSTATS,
  __module__ = 'modules.planning.proto.planning_stats_pb2'
  # @@protoc_insertion_point(class_scope:apollo.planning.PlanningStats)
  ))
_sym_db.RegisterMessage(PlanningStats)


# @@protoc_insertion_point(module_scope)
