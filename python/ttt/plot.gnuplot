#!/usr/bin/gnuplot

plot "< ../avgutil.py run.01" using 1:5 with linespoints title "avg utility",  \
    "< ../maxutil.py run.01" using 1:5 with linespoints title "max utility",  \
    "< ../minutil.py run.01" using 1:5 with linespoints title "min utility",  \
    "< grep ^CHK run.01 | egrep -i 'Epoch starts with.*species' | awk '{print $6/100.;}'" using 1 with lines t "num species"

    
pause -1
