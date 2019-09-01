
Benchmarks
==========

A common complaint about C++ abstractions in HPC is that they hinder compiler optimizations. While that was largely true in the past, a number of developments have improved the situation. More recent C++ standards introduce capabilities and constraints which help the compiler optimize code, and with the widespread adoption of C++ abstraction layers in industry significant work has gone into optimizing the commonly used compilers. To demonstrate that mdspan does not introduce overheads compared to using raw pointers with manual indexing we will show benchmark results generally both for the version using mdspan and an equivalent implementation using raw pointers.  Since the difference in most benchmarks is very small, most figures in this section show overhead of the `mdspan` version over the raw pointer variant. Negative overhead indicates cases where the `mdspan` version was faster.

```{=latex}
\begin{figure*}[!ht]
\centering
\includegraphics[width=0.95\textwidth]{figures/raw_vs_mdspan_normalized.pdf}
\caption{An overview of selected benchmark comparisons of mdspan and raw pointer performance.  Each benchmark is normalized to the average execution time of the raw pointer case.  Details of each of these benchmarks are described in the text.}
\label{raw-vs-mdspan-overview}
\end{figure*}
```

Figure \ref{raw-vs-mdspan-overview} shows a normalized comparison of `mdspan` versions of several selected benchmarks with the same benchmark expressed with raw pointers.  A more thorough elaboration follows.  Most of the benchmarks showed overheads within the measurement noise, and no benchmarks showed overhead greater than 10%. Examination of generated assembly (and, at least in the case of the Intel compiler, optimization reports) indicates similar---usually identical---vectorization of the `mdspan` and raw pointer versions of our benchmarks.

Methodology
-----------

All benchmarks were prepared and executed using the Google Benchmark microbenchmarking support library.[CITATIONNEEDED]  CPU benchmarks were run on [TODO: DESCRIBE mutrino], and GPU benchmarks were run on [TODO: DESCRIBE apollo].  CPU benchmarks were compiled with GCC 8.2.0, Intel ICC 18.0.5, and Clang TODO.  GPU benchmarks were compiled with NVIDIA's NVCC version 10.1, using GCC 5.3.0 as the host compiler.  The source code of all benchmarks is available on the mdspan implementation repository that accompanies this paper (see Implementation section above).  A brief description of each benchmark is also included here for completeness.  These benchmarks tend to focus on the three dimensional use case (which we view as the smallest "relatively non-trivial" number of dimensions), but spot checks with larger numbers of dimensions---up to 10---yielded similar results and led to similar conclusions.

### `Sum3D` Benchmark

Intended as a "simplest possible" benchmark, this benchmark simply sums over all of the entries in a 3D `mdspan`.  The raw pointer version (as with all of the benchmarks) does the same thing, but uses hard-coded index arithmetic.  Both right-most fast-running and left-most fast-running loop structures and layouts were tested (and yielded similar results), and only the right layout, right loop structure results are discussed in this paper, for brevity.  The relevant portion of the source code for this benchmark, for an input `mdspan` named `s` and an output named `sum`, looks like:

```c++
for(ptrdiff_t i = 0; i < s.extent(0); ++i) {
  for (ptrdiff_t j = 0; j < s.extent(1); ++j) {
    for (ptrdiff_t k = 0; k < s.extent(2); ++k) {
      sum += s(i, j, k);
    }
  }
}
```

### `Stencil3D` Benchmark

This benchmark takes the sum of all of the neighboring points in three-dimensional space from an input `mdspan` and stores it in the corresponding entry of the output `mdspan`.  The relevant portion of the source code for this benchmark, for an input `mdspan` named `s`, an output `mdspan` named `o`, and a constant stencil size of type `ptrdiff_t` (taken to be `1` in our benchmarks), looks like:

```c++
for(auto i = d; i < s.extent(0)-d; i ++) {
  for(auto j = d; j < s.extent(1)-d; j ++) {
    for(auto k = d; k < s.extent(2)-d; k ++) {
      value_type sum_local = 0;
      for(auto di = i-d; di < i+d+1; di++) {
        for(auto dj = j-d; dj < j+d+1; dj++) {
          for(auto dk = k-d; dk < k+d+1; dk++) {
            sum_local += s(di, dj, dk);
          }
        }
      }
      o(i,j,k) = sum_local;
    }
  }
}
```


### `TinyMatrixSum` benchmark

This benchmark applies a batched sum operation to large number of small (in this paper, 3x3) matrices, accumulating from the input Nx3x3 `mdspan` into an Nx3x3 `mdspan`.  The relevant portion of the source code for this benchmark, for an input `mdspan` named `s` and an output `mdspan` named `o`, looks like:

```c++
for(ptrdiff_t i = 0; i < s.extent(0); i ++) {
  for(ptrdiff_t j = 0; j < s.extent(1); j ++) {
    for(ptrdiff_t k = 0; k < s.extent(2); k ++) {
      o(i,j,k) += s(i,j,k);
    }
  }
}
```

### `Subspan3D` benchmark

This benchmark performs the same operations as the `Sum3D` benchmark, but uses three calls to `subspan` rather than the normal means of dereferencing an `mdspan`.  It is intended to stress the abstraction overhead (or lack thereof) in the implementation, since `subspan` is the most complex part of the `mdspan` implementation from a C++ perspective.  Note that this is, of course, not the indended use case of the `subspan` function, though it serves as a reasonable worst case proxy.  The relevant portion of the source code for this benchmark, for an input `mdspan` named `s` and an output named `sum`, looks like:

```c++
for(ptrdiff_t i = 0; i < s.extent(0); ++i) {
  auto sub_i = subspan(s, i, all, all);
  for (ptrdiff_t j = 0; j < s.extent(1); ++j) {
    auto sub_i_j = subspan(sub_i, j, all);
    for (ptrdiff_t k = 0; k < s.extent(2); ++k) {
      sum += sub_i_j(k);
    }
  }
}
```

### `MatVec` benchmark


The `MatVec` benchmark performs a simple dense matrix-vector multiply operation; it is aimed at demonstrating the impact of layout choice on performance, particularly in the context of performance portability of parallization across diverse hardware platforms.  Consider this serial implementation:

```c++
for(ptrdiff_t i = 0; i < A.extent(0); ++i) {
  for(ptrdiff_t j = 0; j < A.extent(1); ++j) {
    y(i) += A(i,j) * x(j);
  }
}
```

When parallelizing the outer loop via OpenMP, 
C++17 standard parallel algorithms or CUDA the 
optimal layout depends on the hardware. 
On CPUs the compiler will vectorize the inner loop over 
`j` and thus a unit-stride access on the second dimension 
of `A` is optimal. On GPUs no implicit auto-parallelization 
happens and thus the first dimension must be accessed with 
a unit-stride. Being able to make this layout change in the 
data type, means that the algorithm can stay the same across 
different architectures. 

Results: Compiler Comparison
----------------------------

TODO discussion here

```{=latex}
\begin{figure}[!ht]
\centering
\includegraphics[width=0.45\textwidth]{figures/compiler_comparison.pdf}
\caption{Comparison of overheads, relative to raw pointer implementations, of the serial versions of various benchmarks across different compilers.}
\label{compiler-comparison}
\end{figure}
```

Results: Effect of Static Extents
---------------------------------

TODO

Results: Effect of Layout Abstraction
-------------------------------------

The benchmark in Figure \ref{layout-matvec} was run on the ARM ThunderX2, Intel SkyLake, and NVIDIA TitanV 
platforms using OpenMP parallelization for the 
CPUs and CUDA for the GPU. On the CPU systems 
using `layout_right` for the matrix provides 
the better performance with `layout_left` being 
3x-7x slower. On the GPU, however, the `layout_left` version 
achieves a 10x higher throughput. The results shown represent
performance measured in terms algorithmic memory 
throughput (i.e., count memory accesses in the 
algorithm and divide by runtime).  

```{=latex}
\begin{figure}[!ht]
\centering
\includegraphics[width=0.45\textwidth]{figures/matvec_figure.pdf}
\caption{Comparison of absolute memory bandwidths for the MatVec benchmark with different memory layouts.}
\label{layout-matvec}
\end{figure}
```

Results: Overhead of `subspan`
------------------------------


```{=latex}
\begin{figure}[!ht]
\centering
\includegraphics[width=0.45\textwidth]{figures/subspan_overhead_gcc_and_clang.pdf}
\caption{Comparison of overheads, relative to raw pointer implementations, of the Subspan3D benchmark for GCC and Clang.}
\label{subspan-gcc-and-clang}
\end{figure}
```


For recent versions of GCC and Clang, the results are essentially identical to the raw pointer implementation of `Sum3D`, as shown in Figure \ref{subspan-gcc-and-clang}. (Note that there is no raw pointer implementation of `Subspan3D`, since the whole point is that it would be identical to `Sum3D`).  For ICC 18.0.5, the results showed significant overhead, rendering the GCC and clang results invisible---as much as 400%. (The absolute magnitudes of the raw pointer timings were similiar across all three compilers, so this is a genuine measurement of overhead introduced by the ICC frontend).  Using the more recent ICC 19.0.3.199, we were able to obtain much more reasonable results in C++17 mode.  Interestingly, though, the C++14 results *with the same compiler version* were much more similar to the ICC 18.0.5 results, indicating that the difference arises, at least in part, from more modern C++ abstractions being easier for modern compilers to understand.  These results are shown in Figure \ref{subspan-intel}.

```{=latex}
\begin{figure}[!ht]
\centering
\includegraphics[width=0.5\textwidth]{figures/subspan_overhead_intel.pdf}
\caption{Comparison of overheads, relative to raw pointer implementations, of the Subspan3D benchmark for ICC 19.0.3.199.  Note that this compiler was not available on our primary testing machine, so [DESCRIBE BLAKE] was used for this benchmark.}
\label{subspan-intel}
\end{figure}
```

Results: Effects of Newer C++ Standards
---------------------------------------

TODO
