
Introduction
============

Performance portability is one of the primary concerns of the high-performance computing (HPC) community\cite{DOEPPP}.
Over the last decade in particular, numerous projects\cite{gridcpp2018,alpaka2016,occa2014,raja2014,kokkos2014} have tried to address various challenges associated with it. 
With the recent announcement of the first exascale class platforms introducing architectures which were previously not deployed in the HPC community, 
the urgency and importance of finding solutions to performance portability concerns has increased significantly.
One of the projects which has found significant success in adoption is Kokkos,\cite{kokkos2014,kokkosgithub} a C++ performance-portable programming model originally developed at Sandia National Laboratories, but now maintained by a group spanning four United States National Laboratories as well as the Swiss National Supercomputing Centre. 

Arguably the most significant innovation of the Kokkos project was its `View` data structure, a multi-dimensional array abstraction which addresses concerns of performance portability such as data layout and data access customization.
This array abstraction is now used at the heart of many HPC software projects\cite{kokkosprojects}, and is proving to be critical for meeting the challenges of preparing codebases for the exascale era. 
While maintaining these capabilities in as an HPC-specific solution is workable for now, there are a number of reasons why it would be beneficial to have the core capabilities become part of international language standards.
Doing so would enable tighter integration into other language and library capabilities, such as the proposed ISO C++ Linear Algebra library\cite{wg21_p1673}, make interface compatibility between different HPC products easier, and would further seamless integration with external products used in non-HPC-specific applications.
For example, the proposed ISO C++ Audio library\cite{wg21_p1386} has expressed interest in using this abstraction.

To that end the Kokkos team initiated a collaboration with other stakeholders in the C++ standard, in order to design a multi-dimensional array concept for the ISO C++ standard, which also addresses the concerns of performance portability addressed in the Kokkos `View` abstraction.
The result of that 5+ year process is `std::mdspan`, described herein and proposed to the ISO C++ standard in the proposal P0009\cite{wg21_p0009}. The design allows for a mix of static and dynamic array dimensions, enables control of the data layout, and has customization points to control how data are accessed. The latter includes use cases that involve hardware-specific special load and store paths.

In this work we describe each of the design aspects of `mdspan`, with examples demonstrating their impact for performance and portability concerns, as well as benchmarks of the production-quality reference implementation developed by the authors.
