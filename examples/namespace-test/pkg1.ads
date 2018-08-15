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
		--!subtype to t5
		subtype t5_sub is t5'Base range 0.1 .. 1.1;
		type t6 is mod 2;
		type t7 is array(t1) of t2;
		
		--! This function is implemented somewhere else
		procedure runProgC;
		pragma Import(C,runProgC,"runProgC2");
		
		--procedure getIntFromProgC;
		--pragma Import(C,getIntFromProgC,"getIntFromProgC");
		
		--!default parameter_specification@mode: A_DEFAULT_IN_MODE ---> in
		--! test
		--! \exception ExcpClass asdas dsaddas
		procedure p1(paramIn: IN Integer);--AN_IN_MODE ---> in
		procedure p2(paramInOut: IN OUT Integer);--AN_IN_OUT_MODE ---> inout
		procedure p3(paramOut: OUT Integer);--AN_OUT_MODE ---> out
	
		--! record test 2
		type Constant_type is
		record
			name : String(1..2);
			value : Float;--!< record member is commented
		end record;
		
		--! this task is commented
		task mytask1;
		
		task type mytask2 is
			entry Add(Item : in out Integer); --! test
			entry Remove(Item : in out Integer);
		end mytask2;
		
end Pkg1;