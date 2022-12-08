create table users (
	id integer primary key,
	email text not null unique,
	name text not null,
	password text not null
);

insert into users (email, name, password)
values ('user123@example.com', 'Bagas', 'e606e38b0d8c19b24cf0ee3808183162ea7cd63ff7912dbb22b5e803286b4446');
insert into users (email, name, password)
values ('user456@example.com', 'Dias', 'c670f7b23c1bf997ec890e9d23ea7c016e12b243bdbd151f08baf5f0b86a7c5e');

create table stores (
	id integer primary key,
	name text not null,
	user_id integer not null,
	low_stock_percentage decimal(10, 2) default 1.5,
	foreign key (user_id) references users(id)
);