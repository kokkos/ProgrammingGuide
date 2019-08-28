
Benchmarks
==========

Figure \ref{rawvsmdspan} shows a normalized comparison of `mdspan` versions of several selected benchmarks with the same benchmark expressed with raw pointers.  A more thorough elaboration follows.  Most of the benchmarks showed overheads within the measurement noise, and no benchmarks showed overhead greater than 10%. Examination of generated assembly (and, at least in the case of the Intel compiler, optimization reports) indicates similar---usually identical---vectorization of the `mdspan` and raw pointer versions of our benchmarks.

Methodology
-----------

All benchmarks were prepared and executed using the Google Benchmark microbenchmarking support library.[CITATIONNEEDED]  CPU benchmarks were run on [TODO: DESCRIBE mutrino], and GPU benchmarks were run on [TODO: DESCRIBE apollo].  CPU benchmarks were compiled with GCC 8.2.0, Intel ICC 18.0.5, and Clang TODO.  GPU benchmarks were compiled with NVIDIA's NVCC version 10.1, using GCC 5.3.0 as the host compiler.  The source code of all benchmarks is available on the mdspan implementation repository that accompanies this paper (see Implementation section above).  A brief description of each benchmark is also included here for completeness.  These benchmarks tend to focus on the three dimensional use case (which we view as the smallest "relatively non-trivial" number of dimensions), but spot checks with larger numbers of dimensions---up to 10---yielded similar results and led to similar conclusions.

### `Sum3D` Benchmark

Intended as a "simplest possible" benchmark, this benchmark simply sums over all of the entries in a 3D `mdspan`.  The raw pointer version (as with all of the benchmarks) does the same thing, but uses hard-coded index arithmetic.  Both right-most fast-running and left-most fast-running loop structures and layouts were tested (and yielded similar results), and only the right layout, right loop structure results are discussed in this paper, for brevity.

### `Stencil3D` Benchmark

This benchmark takes the sum of all of the neighboring points in three-dimensional space from an input `mdspan` and stores it in the corresponding entry of the output `mdspan`.

### `TinyMatrixSum` benchmark

This benchmark applies a batched sum operation to large number of small (in this paper, 3x3) matrices, accumulating from the input Nx3x3 `mdspan` into an Nx3x3 `mdspan`.

### `Subspan3D` benchmark

This benchmark performs the same operations as the `Sum3D` benchmark, but uses three calls to `subspan` rather than the normal means of dereferencing an `mdspan`.  It is intended to stress the abstraction overhead (or lack thereof) in the implementation, since `subspan` is the most complex part of the `mdspan` implementation from a C++ perspective.

### `MatVec` benchmark

TODO write this


