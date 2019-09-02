
Conclusions
===========

The ISO-C++ design and a production-oriented implementation of `mdspan` has been presented and benchmarked.
Based on the `View` class template of the Kokkos C++ Performance Portable Programming Model, `mdspan` introduces a multi dimensional array view abstraction into the C++ standard. 
It has been shown that `mdspan` addresses concerns of performance portability, with its layout and accessor abstractions. 
Besides controlling memory access patterns and data access semantics, the abstractions also opens the door for incorporating heterogeneous memory concepts via strong typing.
Using a number of microbenchmarks the paper demonstrates that the implementation of `mdspan` provided by the authors 
has in most cases negligible overhead compared to an implementation with raw pointers.
The implementation can be used with a C++11 standard compliant compiler, and thus can be used with the currently available toolchains on typical supercomputing systems.
The standardization of `mdspan` lays the foundation for further efforts such as a standardized linear algebra,[CITATIONNEEDED] which can help to address future performance portability needs of HPC and heterogeneous computing use cases.

Acknowledgements
================

This work was carried out in part at Sandia National Laboratories.
Sandia National Laboratories is a multimission laboratory managed and operated by National Technology & Engineering Solutions of Sandia, LLC, a wholly owned subsidary of Honeywell International Inc., for the U. S. Department of Energy's National Nuclear Security Administration under contract DE-NA0003525.
