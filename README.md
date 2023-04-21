# Loimos SC23 Run Scripts

Loimos is a codebase for modeling the spread of infectious diseases. The source code for the simulator itself may be found in the main [Loimos project repository](https://github.com/loimos/loimos). This repository contains supplementary scripts used to:
1. Run Loimos in larger many-run experiments.
2. Parse and summarize the resulting output.
3. Generate plots similar to those presented in the paper from those results.

## Setup

These scripts are designed to work in conjunction with Loimos. Thus, in order to make proper usage of them, you should first build Loimos (and its dependencies) from source. The main [Loimos repo](https://github.com/loimos/loimos) contains both the necessary sourcecode and instructions for building it. Additionally, we provided detailed instructions below for installing the same versions of Loimos's dependencies used in the paper.

### Charm++

Charm++ may be installed from source as follows:
1. Clone the Charm++ git repo from GitHub here: [https://github.com/UIUC-PPL/charm](https://github.com/UIUC-PPL/charm).
2. Once the repo is cloned, `cd` into its top-level directory and check out version 7.0.0 with

    ```git checkout v7.0.0```

3. Next, build Charm++. Charm++ has a variety of options and which are best to use varies by system. In general, the build line will look something like this:

    ```./build charm++ <version> smp --with-production --enable-tracing```
  
    Note that you may need to load some module files in order to properly build Charm++ on a cluster. Most clusters will require loading the system MPI, and   Cray clusters will generally require some form of `craype-hugepages`. See below for some examples, or consult the [Charm++ documentation](https://charm.readthedocs.io/en/latest/charm%2B%2B/manual.html#sec-install).
  
    | System              | Version            | Module Line                                              |
    |---------------------|--------------------|----------------------------------------------------------|
    | Cori at NERSC       | `mpi-crayxc`       | `module load rca craype-hugepages8M`                     |
    | Perlmutter at NERSC | `mpi-crayshasta`   | `module load cpu craype-hugepages8M cray-pmi cray-mpich` |
    | Zaratan at UMD      | `mpi-linux-x86_64` | `module load openmpi`                                    |
    | Rivanna at UVA      | `mpi-linux-x86_64` | `module load gompi/9.2.0_3.1.6`                          |

4. Lastly, set the `CHARM_HOME` environment variable so that Loimos is able to find your local installation of Charm++. We recommend adding the following line to either your `~/.bashrc` or `~/.bash_profile` (or similar configuration file for other terminals):
    
    ```export CHARM_HOME="/<full/path/to/install/dir>/charm/<version>"```

    Note that you should *not* append `-smp` to this path in order to build Loimos with SMP; this will be handled by setting a separate environment variable at compile time.

### Protobuf

Protobuf can be installed as follows:
1. Create a separate `install` directory somewhere you have write permissions with `mkdir install`. This is to get around the fact that on most computing clusters, many users will not have sudo permissions. Placing this at the top level of your home directory is often convenient, in which case the full path is given by `$HOME/install`.
2. Download version 3.21.12 of Protobuf here: [https://github.com/protocolbuffers/protobuf/releases/tag/v21.12](https://github.com/protocolbuffers/protobuf/releases/tag/v21.12). We suggest using the C++ version of this release rather than cloning the full repo or using the most recent version as the C++ version has a much simpler build system without as many dependencies, and this is the last release which contains a separate C++ version. You can download this C++ version like so:
    
    ```wget https://github.com/protocolbuffers/protobuf/releases/download/v21.9/protobuf-cpp-3.21.12.tar.gz```

3. Extract the downloaded files and `cd` into the resulting directory: `tar -xzf protobuf-cpp-3.21.12.tar.gz`.
4. Build and install Protobuf as follows:
    ```
    ./configure --prefix=/<full/path/to/install/dir>
    make
    make check
    make install
    ```
5. Lastly, set two environment variables so that Loimos is able to find your local installation of Protobuf. We recommend adding the following lines to either your `~/.bashrc` or `~/.bash_profile` (or similar configuration file for other terminals):
    
    ```
    export PROTOBUF_HOME="/<full/path/to/install/dir>"
    export LD_LIBRARY_PATH="$PROTOBUF_HOME/lib:$LD_LIBRARY_PATH"
    ```

## Weak Scaling Experiment

Now that Loimos is built properly, it is necessary to note that the optimal run-time configuration for Loimos will depend heavily on the system on which it is run. Thus, it is important to note that the scripts outlined below are tuning for running on the Rivanna Cluster at the University of Virginia, and that all `module` commands are given for Rivanna, and may differ when running on another system. With that in mind, the weak scaling experiment outlined in the paper may be carried out as follows:
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