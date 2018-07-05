with Ada.Text_IO;
package body Pkg2.Pkg23 is

	procedure Print_Something23 is 
	begin
	   Ada.Text_IO.Put_Line("Hi from Pkg23");
	end Print_Something23;	
	
	function getInput(x: T; y: T2) return T is
	begin
		return x;
	end getInput;
	
end Pkg2.Pkg23;