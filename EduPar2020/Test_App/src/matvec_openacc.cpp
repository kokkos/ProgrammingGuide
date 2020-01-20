#include <Kokkos_Core.hpp>
#include <assert.h>
#include "helper.hpp"


template <class T>
struct vec_t
{
  T * v;
  vec_t(size_t m){v = (T*) malloc (m * sizeof(T)); assert(v!=NULL);}
  T & operator () (const size_t i) {return v[i];}
};

template <class T>
struct mtrx_t
{
  T * v;
  size_t dim;
  mtrx_t(size_t n, size_t m) {v = (T*) malloc (n * m * sizeof(T)); dim = m; assert(v!=NULL); }
  T & operator () (const size_t i, const size_t j) {return v[j*dim+i];}
};

double run(int argc, char* argv[], Args args)
{
  int N = args.N;
  int M = args.M;
  int nrepeat = args.nrepeat;
  double time;
  {
    typedef vec_t<double> vec_double_t;
    typedef mtrx_t<double> mtrx_double_t;

    vec_double_t y( N );
    vec_double_t x( M );
    mtrx_double_t A( N, M );


  
    // Initialize y vector on host.
    for ( int i = 0; i < N; ++i ) {
      y( i ) = 1;
    }

    // Initialize x vector on host.
    for ( int i = 0; i < M; ++i ) {
      x( i ) = 1;
    }

    // Initialize A matrix on host.
    for ( int j = 0; j < N; ++j ) {
      for ( int i = 0; i < M; ++i ) {
        A( j, i ) = 1;
      }
    }

    #pragma acc data copy(y, x, A, y.v[0:N], x.v[0:M], A.v[0:N*M])
    {

      // Timer products.
      Kokkos::Timer timer;

      for ( int repeat = 0; repeat < nrepeat; repeat++ ) {
        // Application: <y,Ax> = y^T*A*x
        double result = 0;
      
        #pragma acc kernels loop independent reduction(+:result)
        for ( int j = 0; j < N; ++j ) {
          double temp = 0;
          #pragma parallel loop
          for ( int i = 0; i < M; ++i ) {
            temp += A( j, i ) * x( i );
          }
          result += y( j ) * temp;
        }

        // Output result.
        if ( repeat == ( nrepeat - 1 ) ) {
          printf( "  Computed result for %d x %d is %lf\n", N, M, result );
        }
      
        const double solution = (double) N * (double) M;

        if ( result != solution ) {
          printf( "  Error: result( %lf ) != solution( %lf )\n", result, solution );
        }
      }
      // Calculate time.
      time = timer.seconds();
    }
  }
  return time;
}
