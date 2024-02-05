use lucmonet;

select * from facturas;
select * from  detalle_factura;
delete from facturas where id = 1 ; -- >= 245 and id <=  249

delete from detalle_factura where id >= 1 and id <=  403 ;  -- >= 393 and id <=  392


TRUNCATE TABLE secuencia_facturas;
TRUNCATE TABLE detalle_factura;

SET FOREIGN_KEY_CHECKS=0;
TRUNCATE TABLE facturas;
TRUNCATE TABLE pagos;
SET FOREIGN_KEY_CHECKS=1;


ALTER TABLE facturas DROP COLUMN fecha_factura;

ALTER TABLE facturas
ADD fecha_factura DATE;

