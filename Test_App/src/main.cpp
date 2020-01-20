#include <limits>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <sys/time.h>

#include "helper.hpp"

Args parse_args(int argc, char* argv[]);

void checkSizes( int &N, int &M, int &S, int &nrepeat );
double run(int argc, char* argv[], Args args);

int main( int argc, char* argv[] )
{
  Args args  = parse_args (argc, argv);
  
  int N = args.N;
  int M = args.M;
  int nrepeat = args.nrepeat;

  double time = run(argc, argv, args);

  // Calculate bandwidth.
  // Each matrix A row (each of length M) is read once.
  // The x vector (of length M) is read N times.
  // The y vector (of length N) is read once.
  // double Gbytes = 1.0e-9 * double( sizeof(double) * ( 2 * M * N + N ) );
  double Gbytes = 1.0e-9 * double( sizeof(double) * ( M + M * N + N ) );

  // Print results (problem size, time and bandwidth in GB/s).
  printf( "  N( %d ) M( %d ) nrepeat ( %d ) problem( %g MB ) time( %g s ) bandwidth( %g GB/s )\n",
          N, M, nrepeat, Gbytes * 1000, time, Gbytes * nrepeat / time );

  return 0;
}
