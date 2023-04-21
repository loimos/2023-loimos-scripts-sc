# Loimos SC23 Run Scripts

Loimos is a codebase for modeling the spread of infectious diseases. The source code for the simulator itself may be found in the main [Loimos project repository](https://github.com/loimos/loimos). This repository contains supplementary scripts used to:
1. Run Loimos in larger many-run experiments.
2. Parse and summarize the resulting output.
3. Generate plots similar to those presented in the paper from those results.

## Setup

These scripts are designed to work in conjunction with Loimos. Thus, in order to make proper usage of them, you should first build Loimos (and its dependencies) from source. The main [Loimos repo](https://github.com/loimos/loimos) contains both the necessary sourcecode and instructions for building it.

## Weak Scaling Experiment

The weak scaling experiment from the paper can be run on the Rivanna Cluster at the University of Virginia as follows:
1. Clone this repo, such as with

    ```git clone git clone git@github.com:loimos/2023-sc-run-scripts.git```

    and `cd` into the resulting directory.    

2. Load required Python libraries (namely, Pandas) and Gnuplot utilities by running the command

    ```module load python gnuplot```

3. Open `batch/templates/rivanna_template.sh` and update line 20 to reflect where you installed the main Loimos repo. For example, if you installed Loimos in `~/projects/epidemiology`, you should change this line from

```export PROJECT_ROOT=$HOME/biocomplexity/loimos```

to

```export PROJECT_ROOT=$HOME/projects/epidemiology```

Note that the Loimos executable you intent to run should be found in the directory given by `$PROJECT_ROOT/loimos/src`. In the above example, this would be `~/projects/epidemiology/loimos/src`.

4. Run the command

    ```make rivanna-weak-scaling```

    to generate the batch scripts used to run the experiments. Check to make sure that the scripts were generated properly by looking in the `batch` directory for `.sh` files matching those described in the output of the script. We recommend submitting a test job with
    
    ```sbatch batch/rivanna_weak_scaling_on_the_fly_1_nodes.sh```
    
    and checking the output file at `experiments/out/rivanna-weak-scaling/rivanna_weak_scaling_on_the_fly_1_nodes.out` for any errors before proceeding to the next step.

5. The batch scripts can be submitted *en mass* by either:

    a. Running the command

    ```ARGS="-r" make rivanna-weak-scaling```

    b. Copying and pasting the `sbatch` lines printed when running `make rivanna-weak-scaling` into your terminal.

6. Wait until all submitted jobs have been completed.

7. Generate the plot by running

    ```make plots```

    The generated plot will be saved as `figs/weak-rivanna.pdf`.

## License

Loimos is distributed under the terms of the MIT license.

All contributions must be made under the MIT license. Copyrights in the Loimos project are retained by contributors. No copyright assignment is required to contribute to Loimos.

See [LICENSE](https://github.com/loimos/2023-loimos-scripts-sc/blob/develop/LICENSE) for details.

SPDX-License-Identifier: MIT