CREATE TABLE users
(
mail varchar(320) Primary Key,
username varchar NOT NULL,
pwd varchar NOT NULL,
salt varchar NOT NULL,
verified boolean DEFAULT false,
profilepicture BYTEA
);

CREATE TABLE teamboard
(
teamboard_name varchar(320) NOT NULL,
teamboard_id SERIAL PRIMARY KEY
);

CREATE TABLE teamboard_editors
(
teamboard integer references teamboard ON DELETE CASCADE ON UPDATE CASCADE,
editor varchar(320) references Users ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE task
(
part_of_teamboard integer,
	FOREIGN KEY(part_of_teamboard) references teamboard ON DELETE CASCADE ON UPDATE CASCADE,
task_name varchar(320) NOT NULL,
task_id SERIAL,

u_neighbor varchar(320) DEFAULT NULL,
	FOREIGN KEY (part_of_teamboard, u_neighbor) references task ON DELETE CASCADE ON UPDATE CASCADE,
l_neighbor varchar(320) DEFAULT NULL,
	FOREIGN KEY (part_of_teamboard, l_neighbor) references task ON DELETE CASCADE ON UPDATE CASCADE,

Primary Key (part_of_teamboard, task_id)
);


CREATE TABLE task_column
(
part_of_teamboard integer NOT NULL,
part_of_task varchar(320) NOT NULL,
	FOREIGN KEY(part_of_teamboard, part_of_task) references task ON DELETE CASCADE ON UPDATE CASCADE,
name_of_column varchar(320) NOT NULL,
column_id SERIAL,

l_neighbor varchar(320) DEFAULT NULL,
	FOREIGN KEY (part_of_teamboard, part_of_task, l_neighbor) references task_column ON DELETE CASCADE ON UPDATE CASCADE,
r_neighbor varchar(320) DEFAULT NULL,
	FOREIGN KEY (part_of_teamboard, part_of_task, r_neighbor) references task_column ON DELETE CASCADE ON UPDATE CASCADE,

PRIMARY KEY(part_of_teamboard, part_of_task, column_id)
);



CREATE TABLE subtask
(
part_of_teamboard integer NOT NULL,
part_of_task varchar(320) NOT NULL,
name_of_column varchar(320) NOT NULL,
	FOREIGN KEY(part_of_teamboard, part_of_task, name_of_column) references task_column ON DELETE CASCADE ON UPDATE CASCADE,
subtask_name varchar(320),
subtask_id SERIAL,
created date NOT NULL,
deadline date,
color varchar(20),
description varchar,
priority integer DEFAULT 1,
	check (priority BETWEEN 0 and 100),

l_neighbor integer DEFAULT NULL,
	FOREIGN KEY (part_of_teamboard, part_of_task, name_of_column, l_neighbor) references subtask ON DELETE CASCADE ON UPDATE CASCADE,
r_neighbor integer DEFAULT NULL,
	FOREIGN KEY (part_of_teamboard, part_of_task, name_of_column, r_neighbor) references subtask ON DELETE CASCADE ON UPDATE CASCADE,

	PRIMARY KEY(part_of_teamboard, part_of_task, name_of_column, subtask_id)

);

CREATE TABLE tag
(
tag_name varchar(320) PRIMARY KEY,
color varchar(200)
);


CREATE TABLE got_tag
(
teamboard_id integer,
name_of_row varchar(320),
name_of_column varchar(320),
subtask_id integer,
	FOREIGN KEY (teamboard_id, name_of_row, name_of_column, subtask_id) references subtask ON DELETE CASCADE ON UPDATE CASCADE,
tag_name varchar(320) references tag(tag_name) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE does_subtask
(
teamboard_id integer,
name_of_task varchar(320),
name_of_column varchar(320),
subtask_id integer,
	FOREIGN KEY (teamboard_id, name_of_task, name_of_column, subtask_id) references subtask ON DELETE CASCADE ON UPDATE CASCADE,
user_id varchar(320) references users(mail) ON DELETE CASCADE ON UPDATE CASCADE
)