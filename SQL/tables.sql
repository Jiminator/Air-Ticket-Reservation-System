# Jimmy Shong
# Mitchell Zhou

CREATE TABLE airport(
    airport_name varchar(255) NOT NULL,
    city    varchar(255) NOT NULL,
    country varchar(225) NOT NULL,
    type   varchar(15) NOT NULL 
        CHECK (type in ('domestic', 'international', 'both')),
    PRIMARY KEY(airport_name)
);

CREATE TABLE airline(
    airline_name varchar(255) NOT NULL,
    PRIMARY KEY(airline_name)
);

CREATE TABLE airlineStaff(
    username    varchar(255) NOT NULL,
    password    varchar(255) NOT NULL,
    first_name  varchar(35) NOT NULL,
    last_name   varchar(35) NOT NULL,
    date_of_birth   date NOT NULL,
    airline_name    varchar(255) NOT NULL,
    PRIMARY KEY(username),
    FOREIGN KEY(airline_name) REFERENCES airline(airline_name)
);

CREATE TABLE staffPhone(
    username    varchar(255) NOT NULL,
    phone_number    varchar(15) NOT NULL,
    PRIMARY KEY(username, phone_number),
    FOREIGN KEY(username) REFERENCES airlineStaff(username)
);

CREATE TABLE staffEmail(
    username    varchar(255) NOT NULL,
    email   varchar(255) NOT NULL,
    PRIMARY KEY(username, email),
    FOREIGN KEY(username) REFERENCES airlineStaff(username)
);

CREATE TABLE airplane(
    airline_name    varchar(255) NOT NULL,
    airplane_ID     int(10) NOT NULL,
    number_of_seats int NOT NULL,
    manufacturer    varchar(255) NOT NULL,
    age int NOT NULL,
    PRIMARY KEY(airline_name, airplane_ID),
    FOREIGN KEY(airline_name) REFERENCES airline(airline_name),
    index(airplane_ID)
);

CREATE TABLE flight(
    airline_name  varchar(255) NOT NULL,
    flight_number   varchar(10) NOT NULL,
    departure_date_time datetime NOT NULL,
    arrival_date_time   datetime NOT NULL,
    base_price   numeric(12,2) NOT NULL,
    flight_status   varchar(15) NOT NULL
        CHECK (flight_status in ('on-time', 'delayed', 'cancelled')) ,
    departure_airport_name    varchar(255) NOT NULL,
    arrival_airport_name    varchar(255) NOT NULL,
    airplane_ID    int NOT NULL,
    PRIMARY KEY(airline_name, flight_number, departure_date_time),
    FOREIGN KEY(airline_name) REFERENCES airline(airline_name),
    FOREIGN KEY(airplane_ID) REFERENCES airplane(airplane_ID),
    FOREIGN KEY(departure_airport_name) REFERENCES airport(airport_name),
    FOREIGN KEY(arrival_airport_name) REFERENCES airport(airport_name)
);

CREATE TABLE ticket(
    ticket_ID       int NOT NULL,
    airline_name    varchar(255) NOT NULL,
    flight_number   varchar(10) NOT NULL,
    departure_date_time datetime NOT NULL,
    PRIMARY KEY(ticket_ID),
    FOREIGN KEY (airline_name, flight_number, departure_date_time) REFERENCES flight(airline_name, flight_number, departure_date_time) 
);

CREATE TABLE customer(
    email varchar(255) NOT NULL,
    name    varchar(70) NOT NULL,
    password    varchar(255) NOT NULL,
    building_number int NOT NULL,
    street   varchar(35) NOT NULL,
    city   varchar(35) NOT NULL,
    state    varchar(255) NOT NULL,
    phone_number    varchar(15) NOT NULL,
    passport_number varchar(225) NOT NULL,
    passport_expiration date NOT NULL,
    passport_country varchar(225) NOT NULL,
    date_of_birth date NOT NULL,
    PRIMARY KEY(email)
);

create Table purchase(
    ticket_ID int NOT NULL,
    email varchar(225) NOT NULL,
    sold_price numeric(12,2) NOT NULL,
    card_type varchar(225) NOT NULL,
    card_number numeric(16, 0) NOT NULL,
    name_on_card varchar(225) NOT NULL,
    exp_date date NOT NULL,
    purchase_date_time datetime NOT NULL,
    PRIMARY KEY(ticket_ID, email),
    FOREIGN KEY (ticket_ID) REFERENCES ticket(ticket_ID),
    FOREIGN KEY (email) REFERENCES customer(email)
);

create Table interact(
    email varchar(225) NOT NULL,
    airline_name varchar(225) NOT NULL,
    departure_date_time datetime NOT NULL,
    flight_number varchar(10) NOT NULL,
    comment varchar(225) NOT NULL,
    rating int NOT NULL
        check (rating <= 10 and rating >= 1),
    PRIMARY KEY (email, airline_name, departure_date_time, flight_number),
    FOREIGN KEY (email) REFERENCES customer(email),
    FOREIGN KEY (airline_name, flight_number, departure_date_time) REFERENCES flight(airline_name, flight_number, departure_date_time) 
);
