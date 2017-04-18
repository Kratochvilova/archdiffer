drop table if exists comparisons;
drop table if exists differences;

create table comparisons (
  id integer primary key not null,
  time time not null,
  module text not null,
  data1 text not null,
  data2 text not null,
  state text not null
);

create table differences (
  comparison integer not null,
  data text not null,
  diff_type text not null,
  diff text not null,
  FOREIGN KEY(comparison) REFERENCES comparisons(id)
);
