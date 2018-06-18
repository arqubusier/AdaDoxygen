with Ada.Text_IO;
package body Pkg2 is
	pragma Comment ("A comment above 1");
	package body Pkg21 is 
		pragma Comment ("A comment above 2");
		procedure Print_Something_In_Pkg21 is 
		begin
		   Ada.Text_IO.Put_Line("Hi from Pkg21");
		end Print_Something_In_Pkg21;
	end Pkg21;
	
	procedure Print_Something is 
	begin
	   Ada.Text_IO.Put_Line("Hi from Pkg2");
	end Print_Something;
	pragma Comment ("<A comment below 3");
end Pkg2;