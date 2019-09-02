
Design
======

In its most basic form, `mdspan` provides a class template for creating types of objects that represent, but do not own, a contiguous piece (or "span") of memory that is to be treated as a multidimensional entity with one or more dimensional constraints.
Together, these dimensional constraints form a *multi-index domain*.
In the simple case of a two dimensional entity, for instance, this multi-index domain encompasses the row and column indices of what is typically called a matrix.
For instance, 

<!-- Can we run this first example by a few people unfamiliar with mdspan to gauge whether this examples, which is verbose, looks "bad" for us to the uninitiated.-->
```c++
void some_function(float* data) {
  auto my_matrix =
    mdspan<float, dynamic_extent, dynamic_extent>(
      data, 20, 40
    );
  /* ... */
}
```

says to create an object that interprets memory starting at the pointer `data` as a matrix with the shape 20 rows by 40 columns.
Extents can be provided either statically (i.e., at compile-time) or dynamically (as shown above), and static extents can be mixed with dynamic extents:

```c++
void another_function(float* data) {
  auto another_matrix =
    mdspan<float, 20, dynamic_extent>(
      data, 40
    );
  /* ... */
}
```

This code snippet also treats `data` as a 20 by 40 matrix, but the first of these dimensions is "baked in" to the type at compile time---all instances of the type `mdspan<double, 20, dynamic_extent>` will have 20 rows.

The design is greatly simplified by delegating the ownership and lifetime management of the data to orthogonal constructs.
Thus, `mdspan` merely interprets existing memory as a multi-dimensional entity, leaving management of the underlying memory to the user.
This follows a trend of similar constructs recently introduced to C++, such as `string_view` and `span`[CITATIONNEEDED].
Older abstractions also take this approach---iterators, which have been central to C++ algorithm design for decades---are also non-owning entities which delegate lifetime management as a separate concern.[CITATIONNEEDED]

References to entries in these matrices are obtained by giving a multi-index (that is, a set of indices) to `operator()` of the object, which has been overloaded for this purpose:

```c++
// add 3.14 to the value on the row with index 10
// and the column with index 5
some_matrix(10, 5) += 3.14;
// print the value of the entry in the row with
// index 0 and the column with index 38
printf("%f", some_matrix(0, 38));
```

<!-- TOOD: Bryce doesn't like this example, make it better. -->

The length of each dimension is accessed via the `extent` member function.
It takes an index to indicate the dimension.
A loop to multiply all entries of the matrix by a scalar could thus look like this:

```c++
for(int row = 0; row < my_mat.extent(0); ++row)
  for(int col = 0; col < my_mat.extent(1); ++col)
    my_mat(row, col) *= 2.0;
```

Arbitrary slices of an `mdspan` can be taken using the `subspan` function:

```c++
auto my_tens = mdspan<float, 3, 4, 5, 20>(data);
auto my_matrix = subspan(my_tens,
  2, all, pair{2, 4}, 0
);
```

<!-- TODO: Maybe explain this a little more verbosely.-->
The above snippet creates a 4 by 2 matrix sub-view of `my_tens` where the entries `i, j` correspond to index 2 in the first dimension of `my_tens`, index `i` in the second dimension, `j+2` in the third dimension, and `0` in the fourth dimension.
This relatively verbose syntax for slicing was preferred over other approaches because slicing needs can vary substantially across different domains and domain-specific syntax can quite easily be built on top of this verbose and explicit syntax.

Just as `std::string` is actually a C++ alias for `std::basic_string`, `std::mdspan` an alias for `std::basic_mdspan`.
<!-- TODO: Be careful about using the terms customization points, abstractions. What term should we use for what the Allocator paramter of vector is? Figure out what Stepanov calls it.-->
Whereas `std::mdspan` only provides control over the scalar type and the extents, `std::basic_mdspan` exposes more customization points. 
<!-- TODO: s/accessor policy/accessor -->
It is templated on four parameters: the scalar type, the extents object, the layout and the accessor policy. 
In the following sections, we will describe these parameters and their utility in achieving higher performance or better portability. 

## Extents Class Template

In `basic_mdspan` the extents are provided via an `extents` class template.
As with the `mdspan` alias template, the parameters are either static sizes or the `dynamic_extent` tag.

```c++
void some_function(float* data) {
  auto my_matrix =
    basic_mdspan<float, extents<20, dynamic_extent>>(
      data, 40
    );
  /* ... */
}
```

The ability to provide extents statically can help significantly with compiler optimizations.
For example, a compiler may be able to completely unroll small inner loops if the extents are known at compile time.
Knowing exact counts and sizes can also help with vectorization and the optimizer's cost model.
A typical example of this in HPC is operations on a batch of small matrices or vectors, where the length of the dimensions is dictated by a physics property or the way the system was discretized (instead of the problem size).
When this sort of problem interacts with generic code, such information would be lost unless static extents can be part of the `mdspan` type itself.
The `TinyMatrixSum` benchmark (below) provides a proxy for problems with this sort of behavior.


## Layout abstraction

<!--- TODO: Bryce doesn't like "be generic over". Bryce thinks he prefers "parameterize" or some phrasing that uses that term.-->
Modern C++ design requires library authors to orthogonalize certain aspects of the design into customization points that algorithms may be generic over.
The most commonplace example of this is the `Allocator` abstraction[CITATIONNEEDED], which controls memory allocation for standard containers like `std::vector`.
Most algorithms on containers do not change regardless of how the underlying data is allocated, and the `Allocator` abstraction allows those algorithms to be generic over the form of memory allocation used by the container.


An example of one such aspect in the current context is the layout of the underlying data with respect to the multi-index domain.
While a high-quality-of-implementation matrix multiply would definitely specialize for different data layouts, the simplest possible implementation would only need to know how to get and store data associated with a given multi-index into the underlying memory.
This also describes the majority of use cases from the perspective of the caller of such algorithms, where only the semantics of a mathematical matrix multiply are needed regardless of data layout.
The grouping of a single set of mathematical semantics under a common algorithm name (regardless of layout) serves as a conduit for performance portability, and additionally reduces the cognitive load for the writer and particularly the reader of the code.

<!-- TODO: Write a new closing sentence to this paragraph.-->
The canonical example, again with reference to data layout, is the portability of access patterns in code that may run on a latency-optimizer processed (e.g., CPU) or on a bandwidth-optimized processor (e.g., GPU).
GPUs need to coalesce accesses (that is, stride across execution agents) because of the vector nature of the underlying hardware, whereas CPUs want to maximize locality (that is, assign contiguous chunks to the same execution agent) in order to increase cache reuse.


The abstraction for representing data layout generically is called the `LayoutMapping`.
The primary task of the `LayoutMapping` is to represent the transformation of a multi-index into a single, scalar memory offset.
A large number of algorithms on multi-dimensional arrays have semantics that depend only on the data as retrieved through the multi-index domain, indicating that this transformation is a prime aspect for orthogonalization into a customization point.
(Note that many algorithms have *performance* characteristics that depend on this transformation, but the separation of semantic aspects of an algorithm from its performance characteristics is critical to modern programming model design, and the fact that the `LayoutMapping` abstraction promotes this separation is further evidence of its utility as a customization point).

A brief survey of existing practice (such as the BLAS technical standard [CITATIONNEEDED], Eigen [CITATIONNEEDED], and MAGMA [CITATIONNEEDED]) reveals an initial set layout mappings that such an abstraction must support, at minimum:

* row-major or column-major layouts (represented by the `TRANS` parameters in BLAS); these generalize to describe layouts where the fast-running index is left-most or right-most
* strided layouts (represented by the `LD` parameters in BLAS); these generalize to any in a class of layouts that can describe the distance in memory between two consecutive indices in a particular dimension with a constant (specific to that dimension).
* symmetric layouts (e.g., from the `xSYMM` algorithms in BLAS), which also includes generalizations like whether the upper or lower triangle is stored (the `UPLO` parameter in BLAS) and whether the diagonal is stored explicitly, implicitly, or in some separate, contiguous storage.

In addition to similarities, it is also instructive to look at what differences these layout mappings may introduce, which some algorithms may not be generic over.
In general, as many previous researchers have noted [CITATIONNEEDED], the design of generic concepts for customization typically begins with the algorithms, not the data structures.
Much of the design of `LayoutMapping` can be motivated with some very simple algorithms.
Consider an algorithm, `scale`, that takes an `mdspan` and a scalar and multiplies each entry, in place, by the scalar.
For brevity, we will only consider the two-dimensional case here (though much of this motivation can be done even in the one-dimensional case).
If such an algorithm is to be implemented in the simplest possible way---iterating over the rows and column indices and scaling each element---the implementation would fail to meet the semantic requirements of the algorithm for symmetric layouts, since non-diagonal entries reference the same memory.
Thus, it is necessary for certain algorithms to know whether each multi-index in the domain maps to a unique offset in the codomain (the space of all offsets that the mapping can result in).
(An example of an algorithm for which this requirement is *not* needed is `dot_product`.)
The `LayoutMapping` customization expresses this property through the requirement that it provide an `is_unique` method.
Many algorithms are difficult or impossible to implement on general non-unique layouts.
However, in the simple case of `scale` the algorithm *could* be implemented for any layout that is simply *contiguous* by viewing the codomain of the layout as a one-dimensional `mdspan` and scaling each item that way.
Contiguousness is expressed through the requirement of an `is_contiguous` method, and the size of the codomain is expressed through the `required_span_size` required method.
Similarly, as previously observed, many existing implementations (such as the BLAS) can specially handle any layout with regular strides; layout mappings can express whether they are strided using the `is_strided` method.
Finally, all of these aspects need to be expressible statically and dynamically, so for layout mappings where the uniqueness, stridedness, and continguousness are consistently `true` for all instances of the type, the `is_always_unique`, `is_always_strided`, and `is_always_contiguous` hooks are provided in the concept.
These requirements allow, for instance, algorithms that cannot support layouts lacking certain properties to fail at compile time rather than runtime.
The requirements on the `LayoutMapping` concept are summarized in table \ref{layoutreqs}.


```{=latex}
\begin{table}[htbp]
\caption{Requirements on the \texttt{LayoutMapping} Concept}
\begin{center}
\input{layout_policy_table}
\label{layoutreqs}
\end{center}
\end{table}
```


## Accessor abstraction

After several design iterations,[CITEP0009] the authors came to the conclusion that many of the remaining customizations could be encapsulated in the answer to one question: how should the implementation turn an instance of some pointer type and an offset (obtained from the `LayoutMapping` abstraction) into an instance of some reference type? The `AccessPolicy` customization point is designed to provide all of the necessary flexibility in the answer to this question.
Our exploration in this space began with a couple of specific use cases: a non-aliasing `AccessPolicy`, similar to the `restrict` keyword in C,[CITATIONNEEDED] and an atomic `AccessPolicy`, where operations on the resulting reference use atomic operations.
 The former needs to customize the pointer type to include implementation-specific annotations (usually some variant of the C-style `restrict` keyword) that indicate the pointer does not alias pointers derived from other sources within the same context (usually a function scope).
The latter needs to customize the reference type produced by the dereference operation to have it return a `std::atomic_ref<T>`.
(`std::atomic_ref<T>` was merged into the C++ standard working draft during the C++20 cycle, and will likely be officially approved as part of the C++20 balloting process when that process completes sometime in 2020.[CITEP0019]) These requirements immediately led us to include customizable `reference` and `pointer` type names as part of the `AccessPolicy` concept.
Marrying these two customizations could take several forms; one possibility is to have a function that simply takes a `pointer` and returns a `reference`.
However, this requires the `pointer` type to be arbitrarily offsettable---e.g., using `operator+` or `std::advance`.
A simpler approach that removes this requirement is to have a customization point that takes the `pointer` and an offset and returns the `reference` directly.
We chose the latter in order to simplify the requirements on the `pointer` type, and named this required method `access`.

The issue of offsetting a `pointer` to create another `pointer`, while not necessarily separable from the creation of a `reference`, is nonetheless also a concern that `AccessPolicy` needs to address for the implementation of the `subspan` function.
We named this customization with a required method `offset`.
The type of the `pointer` retrieved when arbitrarily offsetting a `pointer` type may not necessarily match the input pointer type---for instance, in the case of an overaligned pointer type used for easy vectorization, a pointer derived from an arbitrary (runtime) offset to this pointer cannot guarantee the preservation of this alignment.
Thus, the `AccessPolicy` is allowed to provide a different `AccessPolicy`, named with the required type name `offset_policy`, that differs in type from itself (and thus, for instance, may differ in its `pointer` type).
Finally, given an arbitrary `pointer` type, the current design requires the ability to "decay" this type into an "ordinary" C++ pointer for compatibility with `std::span`, which does not support `pointer` type customization.
The requirements on the `AccessPolicy` concept are summarized in table \ref{accessreqs}.


```{=latex}
\begin{table}[htbp]
\caption{Requirements on the \texttt{AccessPolicy} Concept}
\begin{center}
\input{access_policy_table}
\label{accessreqs}
\end{center}
\end{table}
```

### Accessor Use Case: Non-aliasing Semantics

As a concrete example, the (trivial) `AccessorPolicy` required to express non-aliasing semantics (similar to the `restrict` keyword and supported in many C++ compilers as `__restrict`) is shown in figure \ref{restrict-accessor}.
This differs from the default accessor (`std::accessor_basic<T>`) only in the definition of the nested type `pointer`.
Interestingly, because the design of `mdspan` requires the `pointer` to be used as a parameter (in `access`) before it is ever turned into a reference, `mdspan` is able to skirt the well-known issues surrounding the meaning of the `restrict` qualifier on a data member of a struct.[CITATIONNEEDED?]

```{=latex}
\begin{figure}[!h]
```
```c++
template <class T>
struct RestrictAccessor {
  using element_type = T;
  using pointer = T* __restrict;
  using reference = T&;
  reference access(pointer p, ptrdiff_t i)
    const noexcept
  { return p[i]; }
  pointer offset(pointer p, ptrdiff_t i)
    const noexcept
  { return p + i; }
};
```
```{=latex}
\caption{An AccessorPolicy that provides an expression of non-aliasing semantics for mdspan.}
\label{restrict-accessor}
\end{figure}
```


### Accessor Use Case: Atomic Access

Frequently in HPC applications, it is necessary to access a region of memory atomically for only a small portion of its lifetime.
Constructing the entity to be atomic for the entire lifetime of the underlying memory, as is done with `std::atomic`, may have unacceptable overhead for many HPC use cases.
As an entity that references a region of memory for a subset of that memory's lifetime, `mdspan` is ideally suited to be paired with a fancy reference type that expresses atomic semantics (that is, all operations on the underlying memory are to be performed atomically by the abstract machine).
With the introduction of `std::atomic_ref` in C++20, all that is needed is an accessor policy that customizes the reference type and provides an `access` method that constructs such a reference.
An implementation of such an `AccessorPolicy` is shown in figure \ref{atomic-accessor}.

```{=latex}
\begin{figure}[!h]
```
```c++
template <class T>
struct AtomicAccessor {
  using element_type = T;
  using pointer = T*;
  using reference = atomic_ref<T>;
  reference access(pointer p, ptrdiff_t i)
    const noexcept
  { return atomic_ref{ p[i] }; }
  pointer offset(pointer p, ptrdiff_t i)
    const noexcept
  { return p + i; }
};
```
```{=latex}
\caption{An AccessorPolicy that provides an expression of non-aliasing semantics for mdspan.}
\label{atomic-accessor}
\end{figure}
```


### Accessor Use Case: Bit-Packing

Similar to the infamous `std::vector<bool>`, the accessor abstraction can be used to return a fancy reference type that references individual bits packed into the bytes of underlying memory.
(Unlike `std::vector<bool>`, though, `std::accessor_basic<bool>` does not do this by default).

### Accessor Use Case: Strong Pointer Types for Heterogeneous Memory Spaces 

Heterogeneity often requires a program to access multiple, potentially disjoint memory spaces.
Thus far, vendor-provided APIs for heterogeneity have tended to represent this memory with plain-old raw pointers.
An important emerging paradigm in modern programming model design is so-called "strong types" (also called "opaque typedefs" or "phantom types"),[CITATIONNEEDED] wherein meaning is opaquely attached to the form of the type (for instance, `distance<double>` and `temperature<double>` would be different concrete types with the same form as `double`).
Applied to heterogeneity, the paradigm would suggest replacing raw pointers with an opaque typedef indicating its compatibility, accessibility, and so on.
This not only introduces safety with respect to memory access by an execution resource, but also allows generic software design strategies where execution mechanisms can be deduced from the type of the data structure.
In `mdspan`, such strong typing can be injected via the customization of the associated pointer type in the `AccessorPolicy`.
Initially, of course, such extensions will be outside of the C++ standard (e.g., OpenMP, HIP, SYCL, and older versions of CUDA), but this design provides a means of forward compatibility if and when it addresses the concept of heterogeneous memory resources in the language.

