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
	
	
	
	procedure p1(paramIn: IN Integer) is 
	begin
	   runProgC;
	end p1;
	
	procedure p2(paramInOut: IN OUT Integer) is 
	begin
	   null;
	end p2;
	
	procedure p3(paramOut: OUT Integer) is 
	begin
	   null;
	end p3;
	
	task body mytask1 is 
		Item : Integer;
	begin
		Item := 1;
	end mytask1;
	
	task body mytask2 is 
	begin
		loop
			accept Add(Item : in out Integer) do
				Item := 1;
			end Add;
			accept Remove(Item : in out Integer) do
				Item := 0;
			end Remove;
		end loop;
	end mytask2;
	
end Pkg1;