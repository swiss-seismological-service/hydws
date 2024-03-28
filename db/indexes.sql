-- should be created through the orm on db creation
create index if not exists ix_hydraulicsample__boreholesection_oid on hydraulicsample (_boreholesection_oid);
create index if not exists ix_hydraulicsample_datetime_value on hydraulicsample (datetime_value);
create index if not exists ix_boreholesection__borehole_oid on boreholesection (_borehole_oid);