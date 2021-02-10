#include <stdio.h>
#include <ctype.h>

int main()
{
  int c;

  while ( (c = getchar()) != EOF ){
    if ( isascii(c) ) {
      putchar(c);
    }
  }
}
