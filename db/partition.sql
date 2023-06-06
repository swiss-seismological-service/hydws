
CREATE TABLE hydraulicsample_default PARTITION OF hydraulicsample DEFAULT;

CREATE OR REPLACE FUNCTION partition_daily_function()
RETURNS TRIGGER AS $$
DECLARE
    partition_date TEXT;
	partition_name TEXT;
	start_of_day TEXT;
	end_of_day TEXT;
BEGIN
    partition_date := to_char(NEW.datetime_value,'YYYY_MM_DD');
 	partition_name := 'hydraulicsample_' || partition_date;
	start_of_day := to_char((NEW.datetime_value),'YYYY-MM-DD');
	end_of_day := to_char((NEW.datetime_value + interval '1 day'),'YYYY-MM-DD');
IF NOT EXISTS
	(SELECT 1
   	 FROM   information_schema.tables 
   	 WHERE  table_name = partition_name) 
THEN
	RAISE NOTICE 'A partition has been created';
	BEGIN
		EXECUTE format(E'CREATE TABLE %I (LIKE hydraulicsample INCLUDING INDEXES)', partition_name);
		EXECUTE format(E'ALTER TABLE %I OWNER TO %s', partition_name, TG_ARGV[0]);
		EXECUTE format(E'NOTIFY hydraulicsample, %L', partition_date);
   	EXCEPTION
		WHEN duplicate_table THEN
			NULL;
	END;
END IF;
EXECUTE format('INSERT INTO %I VALUES ($1.*)', partition_name) USING NEW;
RETURN NULL;
END;
$$
LANGUAGE plpgsql;
