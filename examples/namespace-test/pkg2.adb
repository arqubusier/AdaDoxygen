with Ada.Text_IO;
package body Pkg2 is
	
	package body Pkg21 is 
		
		procedure Print_Something_In_Pkg21 is 
		begin
		   Ada.Text_IO.Put_Line("Hi from Pkg21");
		end Print_Something_In_Pkg21;
	end Pkg21;
	
	procedure Print_Something is 
	begin
	   Ada.Text_IO.Put_Line("Hi from Pkg2");
	end Print_Something;	
	
	procedure Print_Something_Private is 
	begin
	   Ada.Text_IO.Put_Line("private stuff");
	end Print_Something_Private;
	
end Pkg2;