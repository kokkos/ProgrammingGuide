from os.path import split, join as path_join, abspath, dirname, basename
my_directory = dirname(abspath(__file__))

import sys
sys.path.insert(0, "/Users/dshollm/Projects/plotting_tools/source/head")
import json
import attr
from glob import glob
import re
import shutil

from plotting.plottable import *
from plotting.plotters.bar_plot import bar_plot

import matplotlib as mpl
from matplotlib.figure import SubplotParams
from matplotlib import pyplot as plt

data_dir = "/Users/dshollm/Projects/mdspan/etc/p3hpc-19-paper/plots/data"


class MicroBenchmark(DataPoint):
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

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
        except:
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
    
#===============================================================================

class Variable:
    pass

class InputVariable(Variable):
    pass

class OutputVariable(Variable):
    pass

#===============================================================================

@plottable_attribute
class cpu_time(OutputVariable):
    name = "Time"
    value_type = float


@plottable_attribute
class real_time(OutputVariable):
    name = "Time"
    value_type = float
    
@plottable_attribute
class repeats(InputVariable):
    name = "Repeats"
    value_type = int
    default_value = 1

@plottable_derived_variable(
    real_time / repeats / 1000
)
class execution_time(OutputVariable):
    name = "Time (us)"
    
class Sum3DVariable:
    def invalid_if(self, dp):
        return "Sum_3D" not in run_name(dp)

@plottable_attribute
class host_name(InputVariable):
    pass

@plottable_attribute
class source_data_file(InputVariable):
    pass

@plottable_attribute
class run_type(InputVariable):
    pass

@plottable_attribute
class run_name(InputVariable):
    name = "Benchmark Name"

    def format_value(self, val):
        if "Sum_3D" in val:
            # We know how to parse these
            rv = ""
            m = re.search(r'(d?)(\d+)_(d?)(\d+)_(d?)(\d+)', val)
            assert(m is not None)
            x, y, z = map(int, (m[2], m[4], m[6]))
            xd, yd, zd = m[1], m[3], m[5]
            assert("MDSpan" in val or "Raw" in val)
            if "MDSpan" in val:
                run_type = 'mdspan'
            else:
                run_type = 'raw pointer'
                if "Static" not in val:
                    xd, yd, zd = "d", "d", "d"
            note = ""
            if "Cuda" in val:
                note = ", Cuda"
            layout = ""
            if "/left_" in val:
                layout = ", layout left"
            elif "/right_" in val:
                layout = ", layout right"
            return f"{run_type}{layout} ({x}{xd}x{y}{yd}x{z}{zd}){note}"
        else:
            return val
                
@plottable_variable
class sum_3d_layout(InputVariable, Sum3DVariable):
    name = "Layout"
    
    def get_value(self, dp):
        if "/left_" in dp.run_name:
            return "Left"
        elif "/right_" in dp.run_name:
            return "Right"
        elif "Raw" in run_name(dp):
            if "_right/" in run_name(dp):
                return "Right"
            elif "_left/" in run_name(dp):
                return "Left"
            else:
                return None

@plottable_variable
class sum_3d_size(InputVariable, Sum3DVariable):
    
    def invalid_if(self, dp):
        return Sum3DVariable().invalid_if(dp) or (re.search(r'(d?)(\d+)_(d?)(\d+)_(d?)(\d+)', dp.run_name) is None)

    def get_value(self, dp):
        val = dp.run_name
        m = re.search(r'(d?)(\d+)_(d?)(\d+)_(d?)(\d+)', val)
        assert(m is not None)
        x, y, z = map(int, (m[2], m[4], m[6]))
        return x * y * z

@plottable_variable
class sum_3d_iter_order(InputVariable, Sum3DVariable):

    def get_value(self, dp):
        if "Cuda" in dp.run_name:
            return "Cuda"
        if "_right/" in dp.run_name:
            return "Right"
        elif "_left/" in dp.run_name:
            return "Left"
        
@plottable_variable
class data_structure_type(InputVariable):
    name = ""
    value_type = str
    
    def invalid_if(self, dp):
        val = dp.run_name
        return "MDSpan" not in val and "Raw_" not in val
    
    def get_value(self, dp):
        val = dp.run_name
        if "MDSpan" in val:
            return 'mdspan'
        elif "Raw_" in val:
            return 'raw pointer'
        else:
            return None

@plottable_variable
class sum_3d_shape(InputVariable):
    label_x_axis = False
    name = "  "

    def invalid_if(self, dp):
        return re.search(r'(d?)(\d+)_(d?)(\d+)_(d?)(\d+)', dp.run_name) is None

    def get_value(self, dp):
        val = dp.run_name
        m = re.search(r'(d?)(\d+)_(d?)(\d+)_(d?)(\d+)', val)
        x, y, z = map(int, (m[2], m[4], m[6]))
        return f"{x}x{y}x{z}"

@plottable_variable
class sum_3d_dynamicness(InputVariable):
    label_x_axis = False
    name = "  "

    def invalid_if(self, dp):
        return re.search(r'(d?)(\d+)_(d?)(\d+)_(d?)(\d+)', dp.run_name) is None

    def get_value(self, dp):
        val = dp.run_name
        m = re.search(r'(d?)(\d+)_(d?)(\d+)_(d?)(\d+)', val)
        xd, yd, zd = map(lambda v: "S" if v != "d" else "D", (m[1], m[3], m[5]))
        if data_structure_type(dp) == "raw pointer":
            if "Static" not in val:
                xd, yd, zd = "D", "D", "D"
        return f"{xd}x{yd}x{zd}"

@plottable_variable
class sum_3d_type_and_shape(InputVariable):
    label_x_axis = False
    name = "  "
    
    def invalid_if(self, dp):
        return re.search(r'(d?)(\d+)_(d?)(\d+)_(d?)(\d+)', dp.run_name) is None

    def get_value(self, dp):
        val = dp.run_name
        m = re.search(r'(d?)(\d+)_(d?)(\d+)_(d?)(\d+)', val)
        xd, yd, zd = map(lambda v: "S" if v != "d" else "D", (m[1], m[3], m[5]))
        if "MDSpan" in val:
            run_type = 'mdspan'
        else:
            run_type = 'raw pointer'
            if "Static" not in val:
                xd, yd, zd = "D", "D", "D"
        return f"{run_type}\n({xd}x{yd}x{zd})"

@plottable_variable
class compiler(InputVariable):
    name = "Compiler"
    known_compilers = [
        r"(cuda)-(\d+.\d)_gcc-\d.\d.\d",
        r"(gcc)-(\d.\d.\d)",
        r"(intel)-(\d+\.\d+\.\d+)",
        r"(clang)-(\d+\.\d+)",
        r"(gcc)-(\d)"
    ]
    
    def get_value(self, dp):
        for cre in self.known_compilers:
            m = re.search(cre, dp.source_data_file)
            if m:
                return m[0]
        return None
    
    def format_value(self, val):
        for cre in self.known_compilers:
            m = re.search(cre, val)
            if m:
                cname = m[1].capitalize()
                cname = cname.replace("Gcc", "GCC")
                cname = cname.replace("Intel", "ICC")
                return f"{cname} {m[2]}"
        return "<unknown>"

@plottable_variable
class raw_vs_mdspan_plot_test_type(InputVariable):
    name = ""
    value_type = str

    def get_value(self, dp):
        bm = None
        elaboration = ""
        if "Sum_3D_right" in run_name(dp):
            if sum_3d_dynamicness(dp) == "DxDxD" \
                    and compiler(dp) == "intel-18.0.5":
                if sum_3d_layout(dp) == "Right" or data_structure_type(dp) == "raw pointer":
                    bm = "Sum3D"
                    elaboration = "\nSerial"
        elif "Stencil_3D_right" in run_name(dp) or "Stencil_3D/right_" in run_name(dp):
            if sum_3d_dynamicness(dp) == "DxDxD":
                if compiler(dp) == "cuda-10.1_gcc-5.3.0":
                    bm = "Stencil3D"
                    elaboration = "\nCuda"
                elif compiler(dp) == "gcc-8.2.0" and "OpenMP" not in run_name(dp):
                    bm = "Stencil3D"
                    elaboration = "\nSerial (GCC)"
        elif "TinyMatrixSum" in run_name(dp):
            if (data_structure_type(dp) == "mdspan" or "_right/" in run_name(dp)) \
                    and (sum_3d_layout(dp) == "Right" or data_structure_type(dp) == "raw pointer"):
                if "noloop" not in run_name(dp):
                    if sum_3d_dynamicness(dp) == "DxDxD":
                        if "OpenMP" in run_name(dp) and compiler(dp) == "intel-18.0.5":
                            bm = "TinyMatrixSum"
                            elaboration = "\nOpenMP"
                        elif compiler(dp) == "gcc-8.2.0" and "OpenMP" not in run_name(dp):
                            bm = "TinyMatrixSum"
                            elaboration = "\nSerial (GCC)"
                    elif sum_3d_dynamicness(dp) == "SxSxS":
                        if "OpenMP" in run_name(dp) and compiler(dp) == "intel-18.0.5":
                            bm = "TinyMatrixSum"
                            elaboration = " (Static)\nOpenMP"
                        if "OpenMP" not in run_name(dp) and compiler(dp) == "gcc-8.2.0":
                            bm = "TinyMatrixSum"
                            elaboration = " (Static)\nSerial (GCC)"
        if bm is not None:
            return f"{bm}\n{sum_3d_shape(dp).replace('1000000', '1M')}{elaboration}"
        else:
            return "<unknown>"
        
if __name__ == "__main__":
    data = []
    for f in glob(f"{data_dir}/*.json"):
        file_data = MicroBenchmark.load_all_from_json_output(f)
        if file_data is not None:
            data.extend(file_data)


    use_paper_figure_style = True
    plot_sum_3d_cuda = False
    plot_sum_3d_left_right_apollo = False
    plot_sums = False
    make_overview_figure = True

    #================================================================================
    # paper figure style
    if use_paper_figure_style:
        plt.rc('font', family="serif")
        plt.rc('legend', fontsize="small", framealpha=1.0)


    #================================================================================
    if plot_sums:
    #================================================================================

        if plot_sum_3d_cuda:
            for size in (80, 400):
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
    # "Overview" figure
    if make_overview_figure:
        fig, ax = plt.subplots(nrows=1, ncols=1,
            subplotpars=SubplotParams(
                left=0.09,
                right=0.95,
                bottom=0.32
            ),
            figsize=[7.0, 3.0]
        )
        s = get_series(data,
            series_variable=data_structure_type,
            x_variable=raw_vs_mdspan_plot_test_type,
            y_variable=execution_time,
            normalize_by=(data_structure_type == "raw pointer"),
            include_only=(
                (raw_vs_mdspan_plot_test_type != "<unknown>")
                & (run_type != "aggregate")
            )
        )
        print_series_summary(s,
            [var for var in globals().values() if isinstance(var, InputVariable) and not var is source_data_file]
        )
        for ser in s.values():
            ser.y_variable.name = "Time (normalized)"
        
        fig = bar_plot(
            s,
            legend=True,
            error_bars=True,
            fig=fig, ax=ax,
            xticklabels_keywords=dict(rotation=90, fontdict=dict(fontsize=7), family="serif"),
            yticklabels_text_keywords=dict(fontsize=7, family="serif"),
        ).figure
        #ax.set_ylim(0.75, 1.25)
        fig.suptitle(f"Summary of Selected Benchmarks")
        fig.savefig(f"{my_directory}/figures/raw_vs_mdspan_normalized.pdf")
