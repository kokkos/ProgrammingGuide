
Conclusions
===========

The ISO-C++ design and a production-oriented implementation of `mdspan` has been presented and benchmarked.
The implementation has been shown to have negligible overhead compared to the same benchmark implemented with raw pointers in the vast majority of cases, demonstrating conformance with the zero-overhead principal under microbenchmarking conditions.
The process of standardizing a design for `mdspan` can be taken as an archetypical template for integration of performance portable features into international standards---in particular, as a roadmap for framing performance portability as a special case of generic library design.
A number of HPC and heterogeneous computing use cases have been considered, and herein it has been shown that the particular orthogonalization of the design space proposed for `mdspan`---that of layout and accessor abstraction---addresses these concerns in an efficient manner.
The standardization of `mdspan` lays the foundation for future efforts, including standardized linear algebra,[CITATIONNEEDED] which show further promise for addressing performance portability needs in the future.

Acknowledgements
================

This work was carried out in part at Sandia National Laboratories.
Sandia National Laboratories is a multimission laboratory managed and operated by National Technology & Engineering Solutions of Sandia, LLC, a wholly owned subsidary of Honeywell International Inc., for the U. S. Department of Energy's National Nuclear Security Administration under contract DE-NA0003525.
