CREATE OR REPLACE PROCEDURE generate_partitioned_tables (_begindate date, _enddate date)
    AS $$
DECLARE
    _sql text;
    loopdate date DEFAULT _begindate;
BEGIN
    IF _begindate > _enddate THEN
        RAISE EXCEPTION '_begindate should smaller than _end_date';
    END IF;
    IF _begindate is null or _enddate is null THEN
        raise exception '_begindate and _enddate cannot be null';
    end if;
    while loopdate <= _enddate LOOP
        _sql := 'CREATE TABLE IF NOT EXISTS hydraulicsample_'
                    || to_char(loopdate, 'YYYYMMDD')
                    || ' partition of hydraulicsample for values from ('''
                    || loopdate
					|| ''') to (''' 
					|| loopdate + interval '1 day'
					|| ''')';
        RAISE NOTICE '_sql:  %', _sql;
        EXECUTE _sql;
        SELECT
            (loopdate + interval '1 day') INTO loopdate;
    END LOOP;
END
$$
LANGUAGE plpgsql;

-- call generate_partitioned_tables (DATE '2022-01-01', DATE '2022-06-30');
-- call generate_partitioned_tables (DATE '2019-04-01', DATE '2019-05-30');