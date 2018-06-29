with Ada.Text_IO;
package body Pkg1 is
	procedure Print_Something is 
	begin
	   Ada.Text_IO.Put_Line("Hi from Pkg1");
	end Print_Something;
	function getInt(x : Integer) return Integer is
		function getInt2(x2 : Integer) return Integer is
		begin
			return x2;
		end getInt2;
	begin
		return x;
	end getInt;
end Pkg1;