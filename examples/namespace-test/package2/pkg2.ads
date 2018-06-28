--! This is pkg 2
package Pkg2 is
		--! This is a subpackage
		package Pkg21 is
				--! Print Something In Pkg21
				procedure Print_Something_In_Pkg21;
		end Pkg21;
		--! Print something public in package 2 " did you see the double quote?
        procedure Print_Something;

	private
		--! Print something private in package 2
		procedure Print_Something_Private;
end Pkg2; 