drop table if exists products;
create table products (
  id integer primary key autoincrement,
  name text not null,
  price real not null,
  description text not null
);
drop table if exists cart;
create table cart (
  id integer primary key autoincrement,
  name text not null,
  price real not null
);