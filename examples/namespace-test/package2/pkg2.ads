--! This is pkg 2
package Pkg2 is
		--! This is a subpackage
		package Pkg21 is
				--! Print Something In Pkg21
				procedure Print_Something_In_Pkg21;
		end Pkg21;
		--! Print something public in package 2 " did you see the double quote?
        procedure Print_Something;
		
		--! rep test 1
		type t1 is range 1 .. 31;
		--! asd
		for t1'Size use 8;
		for t1'Alignment use 1;
		
		--! rep test 2
		type t2 is 
			record
				Comp1 : Integer;
				Comp2 : Integer;
			end record;
		for t2 use
			record
				Comp1 at 0 range 0 .. 0;
				Comp2 at 0 range 1 .. 1;
			end record;
		

	private
		--! Print something private in package 2
		procedure Print_Something_Private;
end Pkg2;