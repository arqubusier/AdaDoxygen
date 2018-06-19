with Pkg1;
with Pkg2;
with Pkg2.Pkg22;
with Ada.Text_IO; 

use Ada.Text_IO;
use Pkg1;


procedure Prog is
	x : Integer;
begin
	Print_Something;
	Pkg2.Pkg21.Print_Something_In_Pkg21;
	Pkg2.Pkg22.Printer;
	x := getInt(5);
	Pkg2.Print_Something;
	Put_Line("Hi from main");
end Prog;