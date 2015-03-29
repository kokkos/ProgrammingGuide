
PDFENGINE=pdflatex
BIBENGINE=bibtex

TEXFILES=\
	Kokkos_PG_MachineModel.tex \
	Kokkos_PG_Compilation.tex \
	Kokkos_PG_ParallelDispatch.tex \
	Kokkos_PG_HierarchicalParallelism.tex \
	Kokkos_PG_LegacyCodeIntegration.tex \
	Kokkos_PG_ProgrammingModel.tex \
	Kokkos_PG_Initialization.tex \
	Kokkos_PG_Subviews.tex \
	Kokkos_PG_Introduction.tex \
	Kokkos_PG_Ack.tex \
	Kokkos_PG.tex \
	Kokkos_PG.bib

Kokkos_PG.pdf: $(TEXFILES)
	$(PDFENGINE) Kokkos_PG.tex
	$(BIBENGINE) Kokkos_PG	
	$(PDFENGINE) Kokkos_PG.tex
	$(BIBENGINE) Kokkos_PG	
	$(PDFENGINE) Kokkos_PG.tex

clean:
	rm *.pdf *.aux *.log *.toc
