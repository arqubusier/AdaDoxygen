with Ada.Text_IO, Ada.Integer_Text_IO, Ada.Float_Text_IO;
use Ada.Text_IO, Ada.Integer_Text_IO, Ada.Float_Text_IO;

procedure Hello is
	type Integer_Ptr is access Integer;
	Ptr : Integer_Ptr := new Integer;
	nr : Integer;
begin
	nr := 5;
end Hello;