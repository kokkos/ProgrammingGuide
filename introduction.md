
Introduction
============

Performance portability is one of the primary concerns of the high-performance computing (HPC) community.
Over the last decade in particular, numerous projects have tried to address various challenges associated with it. 
The urgency and importance of finding solutions to performance portability concerns has recently increased
significantly with the announcement of the first exascale platforms, which feature at least four different node designs - 
with more to come.
One of the projects which has found significant success in adoption is Kokkos,[CITATIONNEEDED] a C++ performance portable programming model
originally developed at Sandia National Laboratories, but now maintained by a group spanning four US National Laboratories as well
as the Swiss National Supercomputing Centre. 

Arguably the most significant innovation of the Kokkos project was its design of the so called `View` data structure,
a multi-dimensional array abstraction which addresses concerns of performance portability such as data layout and 
data access customization.

This array abstraction is now used at the heart of the data structures for over a hundred HPC software projects, and is proving
to be critical for meeting the challenges of preparing codebases for the exascale era. 
While maintaining these capabilities in as an HPC-specific solution is workable for now, there are a number of reasons why it would be beneficial to have the core
capabilities become part of the international language standards. Doing so would enable tighter integration into other core language capabilities,
make interface compatibility between different HPC products easier, and would further the seamless integration with external products
used in non-HPC-specific applications. 

To that end the Kokkos team initiated a collaboration with other stake holders in the C++ standard, in order to design a multi-dimensional
array concept for the ISO C++ standard, which also addresses the concerns of performance portability addressed in the Kokkos `View` 
abstraction.
The result of that 5+ year process is `std::mdspan`, described herein and proposed to the ISO C++ standard in the proposal
P0009.[CITATIONNEEDED] The design allows for a mix of static and dynamic extents, enables control of the data layout,  and has customization points to
control how data is accessed, including uses cases that involve hardware-specific special load and store paths.

In this work we describe each of the design aspects of `mdspan`, with examples demonstrating their impact for performance and 
portability concerns, as well as benchmarks of the production-quality reference implementation developed by the authors.
