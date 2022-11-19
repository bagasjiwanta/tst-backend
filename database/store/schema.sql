create table if not exists products (
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
	foreign key (category_id) references category(id)
);

create table if not exists categories (
	id integer primary key,
	name varchar(20) not null,
	description varchar(100)
);