use lucmonet;

select * from facturas;
delete from facturas where id = 257 ; -- >= 245 and id <=  249

delete from detalle_factura where id >= 397 and id <=  403 ;  -- >= 393 and id <=  392

select * from  detalle_factura;
TRUNCATE TABLE secuencia_facturas;
TRUNCATE TABLE facturas;
TRUNCATE TABLE detalle_factura;


SET FOREIGN_KEY_CHECKS=0;
TRUNCATE TABLE facturas;
TRUNCATE TABLE pagos;
SET FOREIGN_KEY_CHECKS=1;
