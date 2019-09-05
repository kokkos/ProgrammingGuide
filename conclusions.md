
Conclusions
===========

We have presented both the ISO C++ design and a production-oriented implementation of `mdspan`.
The `mdspan` data structure is based on the `View` class in the Kokkos C++ Performance Portable Programming Model.
`mdspan` introduces a multi-dimensional array view abstraction into the C++ Standard.
The class' layout and accessor abstractions address performance portability concerns.
Besides controlling memory access patterns and data access semantics, the abstractions also open the door for incorporating heterogeneous memory paradigms via strong typing.
Using a number of microbenchmarks, we have demonstrated that our implementation of `mdspan` has (in most cases) negligible overhead, compared to using raw pointers to represent multi-dimensional arrays.
The implementation can be used with a C++11 standard-compliant compiler, and thus can be used with currently available toolchains on typical supercomputing systems.
The standardization of `mdspan` lays the foundation for further efforts, such as standardized linear algebra,\cite{wg21_p1673} which can help to address future performance portability needs of HPC and heterogeneous computing use cases.

Acknowledgments
================

This work was carried out in part at Sandia National Laboratories.
Sandia National Laboratories is a multimission laboratory managed and operated by National Technology & Engineering Solutions of Sandia, LLC, a wholly owned subsidary of Honeywell International Inc., for the U. S. Department of Energy's National Nuclear Security Administration under contract DE-NA0003525.
