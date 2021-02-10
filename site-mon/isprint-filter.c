#include <stdio.h>
#include <ctype.h>

int main()
{
  int c;

  while ( (c = getchar()) != EOF ){
    /*    if ( isascii(c) ) { */
    if ( isprint(c) ) {
      putchar(c);
    }
  }
}
