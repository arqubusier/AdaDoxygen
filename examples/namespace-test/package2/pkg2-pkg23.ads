--! This is pkg 23
package Pkg2.Pkg23 is

	--! Print something public in package 23 " did you see the double quote?
	procedure Print_Something23;
		
	--! A generic function
	--! @tparam T this is a generic type
	--! @tparam T this type is commented twice
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
		
		
end Pkg2.Pkg23;