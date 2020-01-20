#include <Kokkos_Core.hpp>
#include "helper.hpp"

double run(int argc, char* argv[], Args args)
{
  int N = args.N;
  int M = args.M;
  int nrepeat = args.nrepeat;
  double time;

  Kokkos::initialize( argc, argv );
  {
    // typedef Kokkos::Serial   ExecSpace;
    // typedef Kokkos::Threads  ExecSpace;
    // typedef Kokkos::OpenMP   ExecSpace;
    typedef Kokkos::Cuda     ExecSpace;

    // typedef Kokkos::HostSpace     MemSpace;
    // typedef Kokkos::OpenMP        MemSpace;
    typedef Kokkos::CudaSpace     MemSpace;
    // typedef Kokkos::CudaUVMSpace  MemSpace;

    typedef Kokkos::LayoutLeft   Layout;
    //typedef Kokkos::LayoutRight  Layout;
    typedef Kokkos::RangePolicy<ExecSpace>  range_policy;

    // Allocate y, x vectors and Matrix A on device.
    typedef Kokkos::View<double*, Layout, MemSpace>   ViewVectorType;
    typedef Kokkos::View<double**, Layout, MemSpace>  ViewMatrixType;
    ViewVectorType y( "y", N );
    ViewVectorType x( "x", M );
    ViewMatrixType A( "A", N, M );

    // Create host mirrors of device views.
    ViewVectorType::HostMirror h_y = Kokkos::create_mirror_view( y );
    ViewVectorType::HostMirror h_x = Kokkos::create_mirror_view( x );
    ViewMatrixType::HostMirror h_A = Kokkos::create_mirror_view( A );

    // Initialize y vector on host.
    for ( int i = 0; i < N; ++i ) {
      h_y( i ) = 1;
    }

    // Initialize x vector on host.
    for ( int i = 0; i < M; ++i ) {
      h_x( i ) = 1;
    }

    // Initialize A matrix on host.
    for ( int j = 0; j < N; ++j ) {
      for ( int i = 0; i < M; ++i ) {
        h_A( j, i ) = 1;
      }
    }

    // Deep copy host views to device views.
    Kokkos::deep_copy( y, h_y );
    Kokkos::deep_copy( x, h_x );
    Kokkos::deep_copy( A, h_A );

    // Timer products.
    Kokkos::Timer timer;

    for ( int repeat = 0; repeat < nrepeat; repeat++ ) {
      // Application: <y,Ax> = y^T*A*x
      double result = 0; //neutral element
      Kokkos::parallel_reduce( "yAx", range_policy( 0, N ), KOKKOS_LAMBDA ( int j, double &update ) {
        double temp = 0;
        for ( int i = 0; i < M; ++i ) {
          temp += A( j, i ) * x( i );
        }
        update += y( j ) * temp;
      }, result );

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
 
  Kokkos::finalize();

  return time;
}