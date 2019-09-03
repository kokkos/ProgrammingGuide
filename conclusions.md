
Conclusions
===========

The ISO-C++ design and a production-oriented implementation of `mdspan` has been presented and benchmarked.
Based on the `View` data structure of the Kokkos C++ Performance Portable Programming Model, `mdspan` has introduced a multi-dimensional array view abstraction into the C++ standard. 
It has been shown that `mdspan` addresses concerns of performance portability, with its layout and accessor abstractions. 
Besides controlling memory access patterns and data access semantics, the abstraction also has opened the door for incorporating heterogeneous memory paradigms via strong typing.
Using a number of microbenchmarks, this work has demonstrated that the implementation of `mdspan` provided by the authors has (in most cases) negligible overhead compared to an implementation using raw pointers.
The implementation can be used with a C++11 standard-compliant compiler, and thus can be used with currently available toolchains on typical supercomputing systems.
The standardization of `mdspan` lays the foundation for further efforts, such as standardized linear algebra,\cite{wg21_p1673} which can help to address future performance portability needs of HPC and heterogeneous computing use cases.

Acknowledgments
================

This work was carried out in part at Sandia National Laboratories.
Sandia National Laboratories is a multimission laboratory managed and operated by National Technology & Engineering Solutions of Sandia, LLC, a wholly owned subsidary of Honeywell International Inc., for the U. S. Department of Energy's National Nuclear Security Administration under contract DE-NA0003525.
