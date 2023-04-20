load "common.plot"
set terminal pdfcairo enhanced font "Gill Sans,16" linewidth 2 rounded dashed

set style line 100 lt 1 lc rgb "#606060"
set style line 101 lt 0 lc rgb "#606060"

set border 3 back ls 100
set grid noxtics ytics back ls 101
set xtics nomirror
set ytics nomirror

set xlabel "Number of Cores"
set ylabel "Execution Time (s/day)"
set title "Average Runtime per Day for Weak Scaling Runs"
#set key left

set logscale x 2
set logscale y 10
set xtics ("36" 36, "72" 72, "144" 144, "288" 288, "576" 576, "1152" 1152,\
  "1728" 1728, "1980" 1980)
set yrange[1:1000]
set key center bmargin @add_gap

set output "weak-rivanna.pdf"

plot "weak.dat" using ($1*36):4 title "2.304M people/core" with linespoints,\
"weak.dat" using ($1*36):3 title "576k people/core" with linespoints,\
"weak.dat" using ($1*36):2 title "144k people/core" with linespoints
