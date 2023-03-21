CREATE TABLE users
(
mail varchar(320) Primary Key,
username varchar NOT NULL,
pwd varchar NOT NULL,
verified boolean DEFAULT false,
profilepicture BYTEA
);

CREATE TABLE teamboard
(
teamboard_name varchar(320) NOT NULL,
teamboard_id SERIAL PRIMARY KEY,
);

CREATE TABLE teamboard_editors
(
teamboard integer references teamboard(teamboard_id) ON DELETE CASCADE ON UPDATE CASCADE,
editor varchar(320) references Users(mail) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE teamboard_row
(
part_of_teamboard integer references teamboard(teamboard_id) ON DELETE CASCADE ON UPDATE CASCADE,
name_of_row varchar(320) NOT NULL,
u_neighbor varchar(320) DEFAULT NULL,
	FOREIGN KEY (part_of_teamboard, u_neighbor) references teamboard_row ON DELETE CASCADE ON UPDATE CASCADE,
l_neighbor varchar(320) DEFAULT NULL,
	FOREIGN KEY (part_of_teamboard, l_neighbor) references teamboard_row ON DELETE CASCADE ON UPDATE CASCADE,
	
	PRIMARY KEY(part_of_teamboard, name_of_row)
);

CREATE TABLE teamboard_column
(
part_of_teamboard integer references teamboard(teamboard_id) ON DELETE CASCADE ON UPDATE CASCADE,
name_of_column varchar(320) NOT NULL,
l_neighbor varchar(320) DEFAULT NULL,
	FOREIGN KEY (part_of_teamboard, l_neighbor) references teamboard_column ON DELETE CASCADE ON UPDATE CASCADE,
r_neighbor varchar(320) DEFAULT NULL,
	FOREIGN KEY (part_of_teamboard, r_neighbor) references teamboard_column ON DELETE CASCADE ON UPDATE CASCADE,
	
	PRIMARY KEY(part_of_teamboard, name_of_column)
);


CREATE TABLE activity
(
part_of_teamboard integer references teamboard(teamboard_id) ON DELETE CASCADE ON UPDATE CASCADE,
name_of_row varchar(320),
name_of_column varchar(320),
activity_name varchar(320),
activity_id SERIAL,
created date NOT NULL,
deadline date,
color varchar(20),
description varchar,
priority integer DEFAULT 1,
	check (priority BETWEEN 0 and 100),

l_neighbor integer DEFAULT NULL,
	FOREIGN KEY (part_of_teamboard, name_of_row, name_of_column, l_neighbor) references activity(part_of_teamboard, name_of_row, name_of_column, activity_id) ON DELETE CASCADE ON UPDATE CASCADE,
r_neighbor integer DEFAULT NULL,
	FOREIGN KEY (part_of_teamboard, name_of_row, name_of_column, r_neighbor) references activity(part_of_teamboard, name_of_row, name_of_column, activity_id) ON DELETE CASCADE ON UPDATE CASCADE,
	
	PRIMARY KEY(part_of_teamboard, name_of_row, name_of_column, activity_id)

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
activity_id integer,
	FOREIGN KEY (teamboard_id, name_of_row, name_of_column, activity_id) references activity(part_of_teamboard, name_of_row, name_of_column, activity_id) ON DELETE CASCADE ON UPDATE CASCADE,
tag_name varchar(320) references tag(tag_name) ON DELETE CASCADE ON UPDATE CASCADE
);
	
CREATE TABLE does_activity
(
teamboard_id integer,
name_of_row varchar(320),
name_of_column varchar(320),
activity_id integer,
	FOREIGN KEY (teamboard_id, name_of_row, name_of_column, activity_id) references activity(part_of_teamboard, name_of_row, name_of_column, activity_id) ON DELETE CASCADE ON UPDATE CASCADE,
user_id varchar(320) references users(mail) ON DELETE CASCADE ON UPDATE CASCADE
)