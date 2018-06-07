with Ada.Text_IO, Ada.Integer_Text_IO, Ada.Float_Text_IO;
use Ada.Text_IO, Ada.Integer_Text_IO, Ada.Float_Text_IO;

procedure Hello is
	type dataT_type is
		record
			m : Integer;
		end record;

	dataT : dataT_type;

	type dataT_Array is array(1..3) of dataT_type;

	type st_type is
		record
			top : integer;
			items : dataT_Array;
		end record;

	st : st_type;
	
begin
	st.top := 5;
	Put(st.top);
		
end Hello;