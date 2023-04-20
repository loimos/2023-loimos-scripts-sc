GNUPLOT = gnuplot
FLAGS ?=
PREFIX=rivanna

PLOTS=weak-$(PREFIX).pdf \

.PHONY: all
all: $(PLOTS)

weak-$(PREFIX).pdf: weak.plot weak.dat
	$(GNUPLOT) $(FLAGS) $<

CONVERT_SCRIPT=./csv_to_dat.py
%.dat:%.csv $(CONVERT_SCRIPT)
	$(CONVERT_SCRIPT) $<

PARSE_SCRIPT=../convert_experiment_to_csv.py
weak.csv:../experiments/out/$(PREFIX)-weak-scaling $(PARSE_SCRIPT)
	$(PARSE_SCRIPT) $< --prefix $(subst -,_,$(<F)) -o $(realpath .)/weak.csv

.PHONY: clean
clean:
	rm $(PLOTS)
