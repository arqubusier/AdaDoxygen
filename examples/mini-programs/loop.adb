with Ada.Text_IO;
use Ada.Text_IO;

procedure Hello is
	number: Integer;
begin
	number := 0;
	Until_Loop :
		loop
			Put_Line("Hello, world!");
			number := number+1;
			exit Until_Loop when number > 5;
		end loop Until_Loop;
end Hello;