with Ada.Text_IO;
package body Pkg2.Pkg22 is
	procedure Printer is 
	begin
	   Ada.Text_IO.Put_Line("Hi from Pkg2");
	end Printer;
	procedure PrinterPriv is 
	begin
	   Ada.Text_IO.Put_Line("Hi from Pkg2");
	end PrinterPriv;
end Pkg2.Pkg22;