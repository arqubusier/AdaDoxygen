with Ada.Text_IO;
package body Pkg2.Pkg23 is

	procedure Print_Something23 is 
	begin
	   Ada.Text_IO.Put_Line("Hi from Pkg23");
	end Print_Something23;	
	
	function getInput(x: T; y: T2) return T is
	begin
		return x;
	end getInput;
	
	package body Pkg231 is 
		procedure genProd(x: T3) is 
		begin
		   Ada.Text_IO.Put_Line("Hi from Pkg23");
		end genProd;	
	end Pkg231;
	
	
	protected body TestProt is
		entry Add(nr : in out Integer)
			when True is
		begin
			null;
		end Add;
	end TestProt;
	
	protected body TestProt2 is
			procedure protFunc is 
			begin
				null;
			end protFunc;
			
	end TestProt2;
	
end Pkg2.Pkg23;