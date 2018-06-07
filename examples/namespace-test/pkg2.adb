with Ada.Text_IO;
package body Pkg2 is
	procedure Print_Something is 
	begin
	   Ada.Text_IO.Put_Line("Hi from Pkg2");
	end Print_Something;
end Pkg2;