with Pkg1;
with Pkg2;
with Pkg2.Pkg22;
with Ada.Text_IO; 

use Ada.Text_IO;
use Pkg1;

--'''
-- This is the main procedure
--'''
procedure Prog is
	x : Integer;
	package twotwo renames Pkg2.Pkg22;
	
begin

	Print_Something;
	Pkg2.Pkg21.Print_Something_In_Pkg21;
	twotwo.Printer;
	-- Making a function call
	x := getInt(5);
	Pkg2.Print_Something;
	Put_Line("Hi from main");
end Prog;
--The program is ending here