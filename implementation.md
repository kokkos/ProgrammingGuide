
Implementation
==============

This work is accompanied by a production-oriented implementation of the proposed `std::mdspan`, available at [github.com/kokkos/mdspan](https://github.com/kokkos/mdspan), the details of which are discussed in this section.
While the proposal it implements targets C++23, the implementation includes compatibility modes for C++17, C++14, and C++11.
The implementation also includes a couple of macros, `MDSPAN_INLINE_FUNCTION` and `MDSPAN_FORCE_INLINE_FUNCTION`, that can be used to add the appropriate markings to functions and function templates, such as `__device__` for CUDA compatibility.
It has been tested on various versions of numerous C++ compilers, including GCC, Clang, Intel's ICC, Microsoft's MSVC, and NVIDIA's NVCC.
The implementation modestly extends the proposal in several places (mostly with respect to typos in the latter), all of which are documented in the implementation repository (link given above).
