from os.path import split, join as path_join, abspath, dirname, basename
my_directory = dirname(abspath(__file__))

import sys
sys.path.insert(0, "/Users/dshollm/Projects/plotting_tools/source/head")
sys.path.insert(0, my_directory)

import json
from glob import glob
import shutil

from plotting.plottable import *
from plotting.plotters.bar_plot import bar_plot

import matplotlib as mpl
from matplotlib.figure import SubplotParams
from matplotlib import pyplot as plt
from plotting.plottable.combined_data_point import *

from variables import *


class MicroBenchmark(DataPoint):
    
    def __init__(self, **kwargs):
        self._known_aspects = []
        for key, value in kwargs.items():
            self._known_aspects.append(key)
            setattr(self, key, value)

    def __repr__(self):
        rv = f"{type(self).__name__}(\n"
        for k in self._known_aspects:
            rv += f"  {k}={repr(getattr(self, k))},\n"
        rv += ")"
        return rv

    @classmethod
    def from_json(cls, entry, context):
        kwargs = dict()
        if context is not None:
            kwargs.update(context)
        kwargs.update(dict(entry))
        return cls(**kwargs)

    @classmethod
    def load_all_from_json_output(cls, filename):
        file = open(filename)
        try:
            benchmark = json.load(file)
        except json.JSONDecodeError:
            print(f"Error loading json file {filename}")
            shutil.move(filename, f"{dirname(filename)}/broken/{basename(filename)}")
            return None
        rv = []
        assert("context" in benchmark)
        assert("benchmarks" in benchmark)
        for b in benchmark["benchmarks"]:
            if b["run_type"] != "aggregate":
                rv.append(cls.from_json(b, benchmark["context"]))
        for m in rv:
            setattr(m, "source_data_file", filename)
        return rv

def parse_data(
    data_dir = "/Users/dshollm/Projects/mdspan/etc/p3hpc-19-paper/plots/data"
):
    my_data = []
    for f in glob(f"{data_dir}/*.json"):
        file_data = MicroBenchmark.load_all_from_json_output(f)
        if file_data is not None:
            my_data.extend(file_data)
    return my_data

if __name__ == "__main__":

    data = parse_data()

    plot_sum_3d_cuda = False
    plot_sum_3d_left_right_apollo = False
    plot_sums = False
    make_overview_figure = False
    make_compiler_figure = True

    #================================================================================
    if plot_sums:
    #================================================================================

        if plot_sum_3d_cuda:
            for size in (80, 400):
              # noinspection PyTypeChecker
              fig, ax = plt.subplots(nrows=1, ncols=1,
                  subplotpars=SubplotParams(
                      left=0.11,
                      right=0.87,
                      bottom=0.15
                  )
              )
              s = get_series(data,
                  series_variable=sum_3d_layout,
                  x_variable=sum_3d_type_and_shape,
                  y_variable=execution_time,
                  include_only=(
                      (sum_3d_size == size*size*size) 
                      & (sum_3d_iter_order == "Cuda")
                      & (source_data_file.contains("cuda-10.1"))
                      & (source_data_file.contains("apollo"))
                  ),
                  warn_if_different=(host_name,),
              )
              fig = bar_plot(
                  s,
                  legend=True,
                  error_bars=True,
                  fig=fig, ax=ax,
              ).figure
              fig.suptitle(f"Sum3D Benchmark ({size}x{size}x{size})\nCuda 10.1, V100  ")
              fig.savefig(f"{my_directory}/figures/cuda_{size}_sum3d.pdf")

        #================================================================================

        if plot_sum_3d_left_right_apollo:
            for size in (20, 200):
                for cmp, nice_name in {
                  "intel-17.0.1_opt" : "ICC 17.0.1",
                  "gcc-5.3.0" : "GCC 5.3.0"
                }.items():
                    # noinspection PyTypeChecker
                    fig, ax = plt.subplots(nrows=1, ncols=1,
                        subplotpars=SubplotParams(
                            left=0.11,
                            right=0.87,
                            bottom=0.2
                        )
                    )
                    s = get_series(data,
                        series_variable=sum_3d_layout,
                        x_variable=sum_3d_type_and_shape,
                        y_variable=execution_time,
                        include_only=(
                            (sum_3d_size == size*size*size)
                            & (sum_3d_iter_order == "Right")
                            & (source_data_file.contains(cmp))
                            & (source_data_file.contains("apollo"))
                        ),
                        warn_if_different=(host_name,),
                    )
                    fig = bar_plot(
                        s,
                        legend=True,
                        error_bars=True,
                        fig=fig, ax=ax,
                    ).figure
                    fig.suptitle(f"Sum3D Benchmark ({size}x{size}x{size})\nApollo Serial ({nice_name})")
                    fig.savefig(f"{my_directory}/figures/apollo_{cmp}_{size}_sum3d.pdf")
                    
        #================================================================================

        for size in (20, 200):
            # noinspection PyTypeChecker
            fig, ax = plt.subplots(nrows=1, ncols=1,
                subplotpars=SubplotParams(
                    left=0.11,
                    right=0.87,
                    bottom=0.2
                )
            )
            s = get_series(data,
                series_variable=compiler,
                x_variable=sum_3d_type_and_shape,
                y_variable=execution_time,
                include_only=(
                        (sum_3d_size == size*size*size)
                        & (sum_3d_iter_order == "Right")
                        & (sum_3d_layout == "Right")
                        & (~compiler.contains("cuda"))
                        #& (source_data_file.contains("apollo"))
                ),
                warn_if_different=(host_name,),
            )
            print_series_summary(s,
                [var for var in globals().values() if isinstance(var, InputVariable) and not var is source_data_file]
            )
            fig = bar_plot(
                s,
                legend=True,
                error_bars=True,
                fig=fig, ax=ax,
            ).figure
            fig.suptitle(f"Sum3D Benchmark, Layout Right,\n({size}x{size}x{size})")
            fig.savefig(f"{my_directory}/figures/apollo_layout_right_{size}_sum3d.pdf")

    #================================================================================

    if make_compiler_figure:
        cdps = combine_by_same_value_for_variable(
          data,
            (compiler, executable, sum_3d_size)
        )

