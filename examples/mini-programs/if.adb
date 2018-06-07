with Ada.Text_IO;
use Ada.Text_IO;

procedure Hello is
	nr: Integer := 0;
begin
	if nr < 1 then
		Put_Line("nr is less than 1");
	elsif 0 > 1 then
		Put_Line("nr is greater than 1");
	else
		Put_Line("nr is equal to 1");
	end if;
end Hello;