with Ada.Text_IO, Ada.Integer_Text_IO;
use Ada.Text_IO, Ada.Integer_Text_IO;
--konvertera .ads till .h, namespace i header-filen (ex. Ada)
--use -> using i c++
procedure Calculator is
	n1: Integer := 2;
	n2: Integer := 3;
	n3: Integer;
	n4: Integer;
	
	pragma Comment ("Sum integer x and y and return result");
	function Add(x: Integer; y: Integer) return Integer is
		z: Integer;
		
		pragma Comment ("This is a nested function");
		function AddSubFunc(someFloat: Float) return Float is
			z2: Float;
			
			pragma Comment ("This is a nested nested function");
			function AddSubSubFunc(someOtherFloat: Float) return Float is
				z3: Float;
			begin
				z3 := someOtherFloat;
				return z3;
			end AddSubSubFunc;
			
			procedure Print_numbers_nested(nr1: Integer; nr2: Integer) is
			begin
				Put(nr1);
				Put(nr2);
			end Print_numbers_nested;
			
		begin
			z2 := someFloat;
			return z2;
		end AddSubFunc;
		
		type StringTest_type is
		record
			str : String(1..2);
		end record;
		
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
	
	pragma Comment ("Commenting some stuff");
	type Constant_type is
		record
			name : String(1..2);
			value : Float;
		end record;
		
	pi : Constant_type;
	
	pragma Comment ("Prints the input numbers");
	procedure Print_numbers(nr1: Integer; nr2: Integer) is
	begin
		Put(nr1);
		Put(nr2);
	end Print_numbers;
	
	procedure Print_hello is
		x: Integer;
	begin
		Print_numbers(42,1337);
		x := Add(42,1337);
		Put_Line("Hello");
	end Print_hello;
	
	procedure doNothing is
		x: Integer;
	begin
		x := 5;
	end doNothing;
	
begin

	pi.name := "Pi";
	pi.value := 3.14;
	
	n3 := Add(n1,n2);
	doNothing;
	n4 := Sub(n3,n2);
	Put(n4);

end Calculator;