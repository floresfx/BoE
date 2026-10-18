DO $$
DECLARE
  r RECORD;
BEGIN
  FOR r IN 
    SELECT schema_name 
    FROM information_schema.schemata 
    WHERE schema_name LIKE 'tenant_%'
  LOOP
    BEGIN
      EXECUTE format(
        'ALTER TABLE %I.purchase_request_lines ADD COLUMN IF NOT EXISTS quantity_received NUMERIC(14, 4) NOT NULL DEFAULT 0',
        r.schema_name
      );
      RAISE NOTICE 'Actualizado: %', r.schema_name;
    EXCEPTION WHEN OTHERS THEN
      RAISE NOTICE 'Omitido: % (%)', r.schema_name, SQLERRM;
    END;
  END LOOP;
END
$$;