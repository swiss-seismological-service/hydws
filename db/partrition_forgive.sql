CREATE OR REPLACE FUNCTION partition_daily_function() RETURNS trigger
   LANGUAGE plpgsql AS
$$
BEGIN
   RAISE NOTICE 'A partition has been created';
   BEGIN
       /* try to create a table for the new partition */
       EXECUTE
           format(E'CREATE TABLE %I (LIKE hydraulicsample INCLUDING INDEXES)', 'hydraulicsample_' || to_char(NEW.datetime_value, 'YYYYMMDD'));
        /*
        * tell listener to attach the partition
        * (only if a new table was created)
        */
       EXECUTE
           format(E'NOTIFY hydraulicsample, %L', to_char(NEW.datetime_value, 'YYYYMMDD'));
   EXCEPTION
       WHEN duplicate_table THEN
           NULL; -- ignore
   END;
    /* insert into the new partition */
   EXECUTE
       format('INSERT INTO %I VALUES ($1.*)', 'hydraulicsample_' || to_char(NEW.datetime_value, 'YYYYMMDD'))
       USING NEW;
    /* skip insert into the partitioned table */
   RETURN NULL;
END;
$$;

CREATE OR REPLACE TRIGGER partition_daily_function
   BEFORE INSERT
   ON hydraulicsample
   FOR EACH ROW
   WHEN (pg_trigger_depth() < 1)
EXECUTE FUNCTION partition_daily_function();