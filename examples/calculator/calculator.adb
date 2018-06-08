with Ada.Text_IO, Ada.Integer_Text_IO;
use Ada.Text_IO, Ada.Integer_Text_IO;
--konvertera .ads till .h, namespace i header-filen (ex. Ada)
--use -> using i c++
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
	
	type Constant_type is
		record
			name : String(1..2);
			value : Float;
		end record;
		
	pi : Constant_type;
	
	procedure Print_numbers(nr1: Integer; nr2: Integer) is
	begin
		Put(nr1);
		Put(nr2);
	end Print_numbers;
	
	procedure Print_hello is
	begin
		Put_Line("Hello");
	end Print_hello;
	
begin

	pi.name := "Pi";
	pi.value := 3.14;
	
	n3 := Add(n1,n2);
	n4 := Sub(n3,n2);
	Put(n4);

end Calculator;