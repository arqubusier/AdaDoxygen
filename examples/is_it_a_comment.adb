with Ada.Text_IO;
--real 1
package body is_it_a_comment is	
	--"real 2
	--'real 3
	procedure Print_Something is 
	begin
	   --real 4
	   Ada.Text_IO.Put_Line('"--fak\'e1');
	   Ada.Text_IO.Put_Line("--fa\"ke2");
	   
	   Ada.Text_IO.Put_Line('asd--fake3');--real 5
	end Print_Something;
	pragma Comment ("<A comment below 3");
end is_it_a_comment;