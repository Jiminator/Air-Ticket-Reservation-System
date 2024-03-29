# Jimmy Shong
# Mitchell Zhou

#a.
select * from flight
where flight_status != 'cancelled' and departure_date_time > NOW();

/*
|----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| airline_name | flight_number	| departure_date_time |	 arrival_date_time  | base_price | flight_status | departure_airport_name | arrival_airport_name | airplane_ID |
|--------------|----------------|---------------------|---------------------|------------|---------------|------------------------|----------------------|-------------|
|   Jet Blue   |     B6 15	    | 2022-11-22 06:01:00 |	2022-11-22 09:29:00	|   254.00	 |     on-time   |          JFK	      	  |          SFO	     |     320	   |
|--------------|----------------|---------------------|---------------------|------------|---------------|------------------------|------------------------------------|
|   Jet Blue   |     B6 1515	| 2022-11-22 13:30:00 |	2022-11-22 17:05:00	|   254.00	 |     delayed   |          JFK	          |          SFO	     |     420	   |
|----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
*/

#b.
select * from flight
where flight_status = 'delayed'; 

/*
|----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| airline_name | flight_number	| departure_date_time |	 arrival_date_time  | base_price | flight_status | departure_airport_name | arrival_airport_name | airplane_ID |
|--------------|----------------|---------------------|---------------------|------------|---------------|------------------------|----------------------|-------------|
|   Jet Blue   |     B6 1515	| 2022-11-22 13:30:00 |	2022-11-22 17:05:00	|   254.00	 |     delayed   |          JFK	          |          SFO	     |      420	   |
|----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
*/

#c.
select name from purchase natural join customer;
/*
|----------|
|   name   |
|----------|
|   Jimmy  |
|----------|
| Mitchell |
|----------|
*/

#d.
select * from airplane 
where airline_name = 'Jet Blue';

/*
|-------------------------------------------------------------------|
| airline_name | airplane_ID | number_of_seats | manufacturer | age |
|----------------------------------------------|--------------------|
|   Jet Blue   |     320     |       170       |    Airbus    |  20 |
|----------------------------------------------|--------------------|
|   Jet Blue   |     420	 |       250       |    Boeing    |   1 |
|-------------------------------------------------------------------|
*/