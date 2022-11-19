create table if not exists products (
	id integer primary key,
	name varchar(50) not null,
	description varchar(100),
	stock integer default NULL,
	unit varchar(10) not null default 'pcs',
	buy_price decimal(15, 2) default NULL,
	sell_price decimal(15, 2) default NULL,
	minimum_stock integer default NULL,
	category_id integer default NULL,
	foreign key (category_id) references category(id)
);

create table if not exists categories (
	id integer primary key,
	name varchar(20) not null
);