
Multi-dimensional arrays are ubiquitous in high-performance computing (HPC), 
but their absense from the C++ language standard is a long-standing and well-known limitation of its use for HPC.
This paper describes the design and implementation of `mdspan`, 
a proposed C++ standard multidimensional array view that is very likely to be merged into 
the ISO-C++ standard working draft early in the C++23 standardization cycle. 
The proposal is largely inspired by work done in the Kokkos project - a C++ programming model for
Performance Portability deployed by numerous HPC institutions to prepare their code base for 
the exascale class super computing systems. 
This paper describes the final design of mdspan, after a 5-year process to achieve consensus in the
C++ community. 
In particular we will lay out, how the design addresses some of the core challenges of performance portable 
programming, and how its customization point allow a seemless extension into areas not currently 
addressed by the C++ standard, but which are of critical importance in the heterogeneous computing world of todays systems.
Finally, we have provided a production-quality implementation of the proposal in its current (and likely final) form, 
and this work includes several benchmarks of this implementation aimed at demonstrating the zero-overhead nature of the modern design.

