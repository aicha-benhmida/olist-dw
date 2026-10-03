drop table if exists fact_orders;
drop table if exists dim_customers;
drop table if exists dim_date;

create table dim_date(
    date_key int PRIMARY KEY,
    full_date date,
    year int
);
create table dim_customers(
    customer_key serial primary key,
    customer_id varchar(50) unique,
    customer_unique_id varchar(50),
    city varchar(50),
    state varchar(50)
);
create table fact_orders(
    order_id varchar(50) primary key,
    date_key int not null references dim_date(date_key),
    customer_key int not null references dim_customers(customer_key),
    order_revenue numeric(10,2),
    review_score numeric(10,2),
    is_on_time smallint
);