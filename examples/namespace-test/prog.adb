with Pkg1;
with Pkg2;
with Ada.Text_IO; use Ada.Text_IO;

procedure Prog is
	x : Integer;
begin
	Pkg1.Print_Something;
	x := Pkg1.getInt(5);
	Pkg2.Print_Something;
	Put_Line("Hi from main");
end Prog;