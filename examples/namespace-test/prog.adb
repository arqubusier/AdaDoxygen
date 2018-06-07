with Pkg1;
with Pkg2;
with Ada.Text_IO; use Ada.Text_IO;

procedure Prog is 
begin
	Pkg1.Print_Something;
	Pkg2.Print_Something;
	Put_Line("Hi from main");
end Prog;