with Ada.Text_IO;
package body Pkg1 is
	procedure Print_Something is 
	begin
	   Ada.Text_IO.Put_Line("Hi from Pkg1");
	end Print_Something;
end Pkg1;