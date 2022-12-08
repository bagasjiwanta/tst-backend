create table if not exists products (
	id integer primary key,
	name varchar(50) not null,
	description varchar(100),
	stock integer default null,
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

drop table if exists searching;

create virtual table searching
using fts5(id, name, description, category);

insert into searching (id, name, description, category)
select p.id id, p.name name, p.description description, c.name category
from products p inner join categories c on p.category_id = c.id;

select 
id,
highlight(searching, 1, '<b>', '</b>') name,
highlight(searching, 2, '<b>', '</b>') description,
highlight(searching, 3, '<b>', '</b>') category
from searching
where searching match 's*'
order by rank