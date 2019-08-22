#!/usr/bin/env sh

function section_to_tex() {
  pandoc -f markdown-auto_identifiers+raw_tex -t latex ${mydir}/../$1.md > $mydir/$1.tex
}


mydir=$(cd $(dirname $0) && pwd)
section_to_tex abstract
section_to_tex design
section_to_tex implementation
section_to_tex benchmarks
section_to_tex conclusions
section_to_tex introduction
cd $mydir
pdflatex $mydir/paper.tex
pdflatex $mydir/paper.tex
