.PHONY:plots
plots:
	$(MAKE) -C figs

.PHONY:rivanna $(RIVANNA_RUNS)
rivanna: $(RIVANNA_RUNS)

rivanna-weak-scaling:
	mkdir experiments/out/rivanna-weak-scaling -p
	python3 generate_batch_scripts.py batch/templates/rivanna_template.sh experiments/specs/rivanna-weak-scaling.csv batch/ rivanna-weak-scaling  --time 30 --output-name "rivanna_weak_scaling_{DATASET}_{NUM_NODES}_nodes" $(ARGS)
