create table users (
	id integer primary key,
	email varchar(100) not null,
	name varchar(50) not null,
	password varchar(300) not null
)

create table store (
	id varchar(50) primary key,
	name varchar(100),
	user_id integer not null,
	foreign key (user_id) references users(id)
)

create table product (
	id integer primary key,
	code varchar(50) unique,
	name varchar(50),
	stock integer default 0,
	buy_price decimal(15, 2),
	buy_account varchar(10),
	buy_tax varchar(10),
	sell_price decimal(15, 2),
	sell_account varchar(10),
	sell_tax varchar(10),
	minimum_stock integer default 0,
	category_id integer,
	store_id integer not null,
	foreign key (category_id) references category(id),
	foreign key (store_id) references store(id)
)

create table category (
	id integer primary key,
	name varchar(20),
	description varchar(100)
)