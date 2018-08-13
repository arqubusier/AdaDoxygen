--! This is pkg 23
package Pkg2.Pkg23 is

		--! Print something public in package 23 " did you see the double quote?
		procedure Print_Something23;
			
		--! A generic function
		--! @tparam T this is a generic type
		--! @tparam T <i>type T is (<>);</i>
		--! @tparam T2 another generic type
		generic
			Max : Positive;
			type T is (<>);
			type T2 is (<>);
		function getInput(x: T; y: T2) return T;
		
		--! This is a generic package
		--! @tparam PT this is a generic type for a package
		generic
			type PT is (<>);
		package Pkg231 is
			generic
				type T3 is (<>);
			procedure genProd(x: T3);
		end Pkg231;
		
		type tLim is limited private;
		
		type tEnum is (Red, Green, Blue);
		for tEnum use (Red => 10, Green => 20, Blue => 30);
	
	private
	
		type tLim is record
			I : Integer;
		end record;
		
		
end Pkg2.Pkg23;