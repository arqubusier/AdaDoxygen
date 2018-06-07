with Ada.Text_IO, Ada.Integer_Text_IO;
use Ada.Text_IO, Ada.Integer_Text_IO;

procedure Calculator is
	n1: Integer := 2;
	n2: Integer := 3;
	n3: Integer;
	n4: Integer;
	
	function Add(x: Integer; y: Integer) return Integer is
		z: Integer;
	begin
		z := x + y;
		return z;
	end Add;
	
	function Sub(a: Integer; b: Integer) return Integer is
		z: Integer;
	begin
		z := a - b;
		return z;
	end Sub;
	
begin

	n3 := Add(n1,n2);
	n4 := Sub(n3,n2);
	Put(n4);

end Calculator;