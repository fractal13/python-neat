#!/usr/bin/gnuplot

#plot "run.00" using 1:5 with lines, \
#    "run.01" using 1:5 with lines, \
#    "run.02" using 1:5 with lines, \
#    "run.03" using 1:5 with lines, \
#    "run.04" using 1:5 with lines t "04-utility(.01 per move)", \
#    "run.05" using 1:5 with lines t "05-utility(.01 per move)", \


plot "< ./avgutil.py killme" using 1:5 with linespoints title "avg utility(1/81 per move)",  \
    "< ./maxutil.py killme" using 1:5 with linespoints title "max utility(1/81 per move)",  \
    "< ./minutil.py killme" using 1:5 with linespoints title "min utility(1/81 per move)",  \
    "< grep ^CHK killme | egrep -i 'Epoch starts with.*species' | awk '{print $6/100.;}'" using 1 with lines t "num species"

    
pause -1
