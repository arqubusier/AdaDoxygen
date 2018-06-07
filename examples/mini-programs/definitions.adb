with Ada.Text_IO, Ada.Integer_Text_IO, Ada.Float_Text_IO;
use Ada.Text_IO, Ada.Integer_Text_IO, Ada.Float_Text_IO;

procedure Hello is
	i1: Integer := 2;
	i2: Integer;
	
	s1: String(1..4) := "str1";
	s2: String(1..4);
	
	arr1 : array(1..3) of Integer;
	arr2 : array(1..5) of Integer;
	arr3 : array(-2..2) of Integer;
	
begin
	i2 := 3;
	s2 := "str2";
	
	for i in 1 .. 3 loop
		arr1(i) := i + 15;
	end loop;
	for i in 1 .. 3 loop
		Put(arr1(i));
	end loop;
	
	arr2 := (1 => 4, 2 => 16, 3 => 25, others => 0);
	for i in 1 .. 5 loop
		Put(arr2(i));
	end loop;
	
	arr3 := (-10,15,3,8,200);
	for i in -2..2 loop
		Put(arr3(i));
	end loop;
		
end Hello;