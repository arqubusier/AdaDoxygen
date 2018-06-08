#include <iostream>
/*! @file same_fn_as_namespace.cpp */

using namespace std;

int addition ()
{
  return 5;
}

namespace addition
{
	double hello()
	{
		return 13.37;
	}
}

int main()
{
    cout << "Hello, World! ";
	int sum = addition ();
	cout << "The sum of 5 is " << sum;
  
    return 0;
}