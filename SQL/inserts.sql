# Jimmy Shong
# Mitchell Zhou

# a.
INSERT INTO airline (airline_name) VALUES ('Jet Blue');
INSERT INTO airline (airline_name) VALUES ("United Airlines");

# b.
INSERT INTO airport (airport_name, city, country, type) 
VALUES ("JFK", "Queens", "USA", "both");

INSERT INTO airport (airport_name, city, country, type) 
VALUES ("SFO", "San Francisco", "USA", "both");

INSERT INTO airport (airport_name, city, country, type) 
VALUES ("PVG", "Shanghai", "China", "both");

# c.
INSERT INTO airlineStaff VALUES ('js11718', '12345', 'Jimmy', 'Shong', '2002-10-08', 'Jet Blue');
INSERT INTO airlineStaff VALUES ('mz2909', '6789', 'Mitchell', 'Zhou', '2002-05-29', 'United Airlines');
INSERT INTO staffEmail VALUES ('js11718', 'js11718@nyu.edu');
INSERT INTO staffEmail VALUES ('mz2909', 'mz2909@nyu.edu');


# d.
INSERT INTO customer (email, name, password, building_number, street, city, state, phone_number, passport_number, passport_expiration, passport_country, date_of_birth) VALUES ("js11718@nyu.edu", "Jimmy", "12345", "4033", "Jay Street", "Brooklyn", "NY", "5556123456", "48274852", '2024-09-18', 'USA', '2002-10-08');
INSERT INTO customer (email, name, password, building_number, street, city, state, phone_number, passport_number, passport_expiration, passport_country, date_of_birth) VALUES ("mz2909@nyu.edu", "Mitchell" , "root", "4033", "Jay Street", "Brooklyn", "NY", "7572641911", "84728490", '2024-12-09', 'USA', '2002-05-29');
INSERT INTO customer (email, name, password, building_number, street, city, state, phone_number, passport_number, passport_expiration, passport_country, date_of_birth) VALUES ("ratan@nyu.edu", "Ratan","ratanDey123", "849", "Jay Street", "Brooklyn", "NY", "6469973600", "10974629", '2024-09-18', 'USA', '2000-11-18');

# e.
INSERT INTO airplane (airline_name, airplane_ID, number_of_seats, manufacturer, age)
VALUES ("Jet Blue", 320, 170, "Airbus", 20);
INSERT INTO airplane (airline_name, airplane_ID, number_of_seats, manufacturer, age)
VALUES ("Jet Blue", 420, 250, "Boeing", 1);
INSERT INTO airplane (airline_name, airplane_ID, number_of_seats, manufacturer, age)
VALUES ("United Airlines", 76, 80, "Airbus", 12);
INSERT INTO airplane (airline_name, airplane_ID, number_of_seats, manufacturer, age)
VALUES ("United Airlines", 21, 120, "Boeing", 6);

# f.
INSERT INTO flight(airline_name, flight_number, departure_date_time, arrival_date_time, base_price, flight_status, departure_airport_name, arrival_airport_name, airplane_ID) 
VALUES ('Jet Blue', 'B6 15', '2022-11-22 06:01:00', '2022-11-22 09:29:00', 254, 'on-time', 'JFK', 'SFO', 320);

INSERT INTO flight(airline_name, flight_number, departure_date_time, arrival_date_time, base_price, flight_status, departure_airport_name, arrival_airport_name, airplane_ID) 
VALUES ('Jet Blue', 'B6 1515', '2022-11-22 13:30:00', '2022-11-22 17:05:00', 254, 'delayed', 'JFK', 'SFO', 420);

INSERT INTO flight(airline_name, flight_number, departure_date_time, arrival_date_time, base_price, flight_status, departure_airport_name, arrival_airport_name, airplane_ID) 
VALUES ('United Airlines', 'UA 891', '2023-07-11 04:35:00', '2023-07-11 08:30:00', 12123, 'cancelled', 'SFO', 'PVG', 21);

# g.
INSERT INTO ticket(ticket_ID, airline_name, flight_number, departure_date_time)
VALUES (2468, 'Jet Blue', 'B6 15', '2022-11-22 06:01:00');

INSERT INTO ticket(ticket_ID, airline_name, flight_number, departure_date_time)
VALUES (1357, 'Jet Blue', 'B6 1515', '2022-11-22 13:30:00');

INSERT INTO purchase(ticket_ID, email, sold_price, card_type, card_number, name_on_card, exp_date, purchase_date_time)
VALUES (2468, 'js11718@nyu.edu', 254, 'credit', 1234567890123456, 'Jimmy Shong', '2029-11-22', '2022-11-21 08:30:00');

INSERT INTO purchase(ticket_ID, email, sold_price, card_type, card_number, name_on_card, exp_date, purchase_date_time) 
VALUES (1357, 'mz2909@nyu.edu', 254, 'debit', 3728193847283410, 'Mitchell Zhou', '2024-12-22', '2022-11-21 11:33:00');
