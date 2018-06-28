package Pkg1 is
        procedure Print_Something;
		function getInt(x : Integer) return Integer;
		--!this type is commented
		type t1 is (alt1, alt2, alt3);
		type t2 is range 1 .. 10;
		
		type t3 
		is new t2 
		range 2 .. 8;
		
	private
		
		--subtype t4 is Integer (t2);
		type t5 is digits 4 range 0.0 .. 1.0;
		type t6 is mod 2;
		type t7 is array(t1) of t2;
		
end Pkg1;