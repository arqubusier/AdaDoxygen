with Ada.Text_IO, Ada.Integer_Text_IO;
use Ada.Text_IO, Ada.Integer_Text_IO;

procedure Hello is
	n1: Integer := 2;
	n2: Integer := 3;
	n3: Integer;
	
	function Sum(x: Integer; y: Integer) return Integer is

		function Sum_Nested(x: Integer; y: Integer) return Integer is
			z: Integer;
		begin
			z := x + y;
			return z;
		end Sum_Nested;
		
		begin
		return Sum_Nested(x,y);
	end Sum;
	
begin
	n3 := Sum(n1,n2);
	Put(n3);
end Hello;