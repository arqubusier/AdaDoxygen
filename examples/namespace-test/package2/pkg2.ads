pragma Comment ("This is pkg 2");
package Pkg2 is
		pragma Comment ("This is a subpackage");
		package Pkg21 is
				pragma Comment ("Print Something In Pkg21");
				procedure Print_Something_In_Pkg21;
		end Pkg21;
		pragma Comment ("Print something public in package 2");
        procedure Print_Something;

	private
		pragma Comment ("Print something private in package 2");
		procedure Print_Something_Private;
end Pkg2;