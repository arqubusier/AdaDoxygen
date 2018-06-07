with Ada.Text_IO;
use Ada.Text_IO;

procedure Hello is
	nr: Integer := 2;
begin
	case nr is
	  when 0 => Put_Line("zero");
	  when 1 => Put_Line("one");
	  when 2 => Put_Line("two");
	  when others => Put_Line("nr is not 0, 1 or 2");
	end case;
end Hello;