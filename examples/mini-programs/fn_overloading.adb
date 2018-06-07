with Ada.Text_IO, Ada.Integer_Text_IO, Ada.Float_Text_IO;
use Ada.Text_IO, Ada.Integer_Text_IO, Ada.Float_Text_IO;

procedure Hello is
	n1: Integer := 2;
	n2: Integer;
	n3: Integer;
	n4: Integer;
	
	inFloat: Float := 2.3;
	outFloat: Float;	
	
	function Sum(x: Float) return Float is
		z: Float;
	begin
		z := x;
		return z;
	end Sum;
	
	function Sum(x: Integer) return Integer is
		z: Integer;
	begin
		z := x;
		return z;
	end Sum;
	
	function Sum(x: Integer; y: Integer) return Integer is
		z: Integer;
	begin
		z := x + y;
		return z;
	end Sum;
	
	function Sum(x: Integer; y: Integer; Z: Integer) return Integer is
		o: Integer;
	begin
		o := x + y + z;
		return o;
	end Sum;
	
begin
	n2 := Sum(n1);
	
	outFloat := Sum(inFloat);
	Put(outFloat);
	
	n3 := Sum(n1,n2);
	n4 := Sum(n1,n2,n3);
	Put(n4);

end Hello;