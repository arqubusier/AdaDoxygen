with Ada.Text_IO, Ada.Integer_Text_IO;
use Ada.Text_IO, Ada.Integer_Text_IO;

procedure Hello is
	n1: Integer := 2;
	n2: Integer := 3;
	n3: Integer;
	global_int: Integer := 42;
	
	function Print_Something(x: Integer) return Integer is
	begin
		Put_Line("hello");
		return 9;
	end Print_Something;
	
	function Sum2(x: Integer; y: Integer) return Integer is
	
		function Print_Something2(x: Integer) return Integer is
		begin
			Put_Line("hello2");
			return 9;
		end Print_Something2;
		
		function Sum(x: Integer; y: Integer) return Integer is
			z: Integer;
		begin
			z := x + y;
			Put_Line("Hej inne");
			z := Print_Something(10);-- cannot reach
			z := Print_Something2(10);
			Put(global_int+1); --can reach
			return z;
		end Sum;
		
		
			
		begin
		Put_Line("Hej ute");
		Put(global_int);
		return Sum(x,y);
	end Sum2;
	
begin
	n3 := Sum2(n1,n2);
	Put(n3);
end Hello;