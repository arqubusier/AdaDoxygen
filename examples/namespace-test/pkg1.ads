--! asd test
--! asd line 2
package Pkg1 is
        procedure Print_Something;
		--! returns a Integer
		function getInt(x : Integer) return Integer;
		--!this type is commented
		type t1 is (alt1, alt2, alt3);
		type t2 is range 1 .. 10;
		
		type t3 
		is new t2 
		range 2 .. 8;
		
		--! record test
		type StringTest_type is
		record
			str : String(1..2);
		end record;
		
	private
		
		--!t5 is also commented....
		type t5 is digits 4 range 0.0 .. 1.0;
		type t6 is mod 2;
		type t7 is array(t1) of t2;
		
	
		--! record test 2
		type Constant_type is
		record
			name : String(1..2);
			value : Float;
		end record;
		
end Pkg1;