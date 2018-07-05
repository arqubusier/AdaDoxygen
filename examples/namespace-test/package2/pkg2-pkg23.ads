--! This is pkg 23
package Pkg2.Pkg23 is

	--! Print something public in package 23 " did you see the double quote?
	procedure Print_Something23;
		
	generic
		type T is (<>);
		type T2 is (<>);
	function getInput(x: T; y: T2) return T;
		
		
end Pkg2.Pkg23;