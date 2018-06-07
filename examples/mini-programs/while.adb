with Ada.Text_IO;
use Ada.Text_IO;

procedure Hello is
	number: Integer;
begin
	number := 0;
	while number < 4 loop
		Put_Line("Hello, world!");
		number := number+1;
	end loop;
end Hello;