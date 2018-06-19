/*! @file calculator.cpp */
using namespace Ada::Text_IO::Ada::Integer_Text_IO;


namespace __Calculator {
namespace __Add {
namespace __AddSubFunc {

/*! This is a nested nested function */
Float AddSubSubFunc (Float someOtherFloat) {
Float z3;

}

void Print_numbers_nested (Integer nr1, Integer nr2) {
Put(nr1);
Put(nr2);

}

}
/*! This is a nested function */
Float AddSubFunc (Float someFloat) {
using namespace _AddSubFunc;
Float z2;

}

struct StringTest_type{
	String str;
};

void TestFuncStruct (StringTest_type str_struct_arg) {
Put();

}

}
/*! Sum integer x and y and return result */
Integer Add (Integer x, Integer y) {
using namespace _Add;
Integer z;
StringTest_type str_struct;

}

/*! The sub-func */
Integer Sub (Integer a, Integer b) {
Integer z;

}

/*! Commenting some stuff */
struct Constant_type{
	String name;
	Float value;
};

/*! Prints the input numbers */
void Print_numbers (Integer nr1, Integer nr2) {
Put(nr1);
Put(nr2);

}

/*! Prints hello */
void Print_hello () {
Integer x;
Natural n;
Print_numbers(42,1337);
(void)Add(42,1337);
Put_Line("Hello");

}

void doNothing () {
Integer x;

}

}
void Calculator () {
using namespace _Calculator;
Integer n1;
Integer n2;
Integer n3;
Integer n4;
Constant_type pi;
(void)Add(n1);
(void)Add(n2,n2);
doNothing();
(void)Sub(n3,n2);
Put(n4);

}
