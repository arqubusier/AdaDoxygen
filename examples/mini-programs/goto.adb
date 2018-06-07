with Ada.Text_IO;
use Ada.Text_IO;

procedure Hello is
	number: Integer;
begin
	goto label_name;
	number := 0;
	while number < 4 loop
		Put_Line("Hello, world!");
		number := number+1;
	end loop;
<<label_name>>
	Put_Line("Was 'Hello, world!' printed?");
end Hello;