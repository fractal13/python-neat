#!/bin/bash
file=utttstartgenes
trait=1;
innov=1;
rm -f $file

# HEAD
# traits
cat > $file <<EOF
genomestart 1
trait 1 0.1 0 0 0 0 0 0 0
trait 2 0.2 0 0 0 0 0 0 0
trait 3 0.3 0 0 0 0 0 0 0
EOF

num_bias=1      # need a bias ?
num_input=171   # 81 each board position for you, 81 each board position me, 9 for which is next board to play on
num_output=18   # 9 for which board, 9 for which position
# BIAS
a=1
b=$num_bias
for i in `seq $a $b`; do
    echo node $i 0 1 3 >> $file
done

# INPUT
((a = num_bias + 1))
((b = num_bias + num_input))
for i in `seq $a $b`; do
    echo node $i 0 1 1 >> $file;
done

# OUTPUT
((a = num_bias + num_input + 1))
((b = num_bias + num_input + num_output))
for i in `seq $a $b`; do
    echo node $i 0 0 2 >> $file;
done

# # LINKS (all BIAS/INPUT to all OUTPUT)
# ((a = 1))
# ((b = num_bias + num_input))
# ((c = num_bias + num_input + 1))
# ((d = num_bias + num_input + num_output))

# LINKS (from BIAS to all OUTPUT)
((a = 1))
((b = 1))
((c = num_bias + num_input + 1))
((d = num_bias + num_input + num_output))
for i in `seq $a $b`; do
    for j in `seq $c $d`; do
	echo gene $trait $i $j 0.0 0 $innov 0 1 >> $file;
	((innov = innov + 1));
	((trait = trait + 1));
	if [ $trait -gt 3 ]; then
	    trait=1;
	fi;
    done;
done

# LINKS (from NEXTBOARD to all OUTPUT)
((a = num_bias + num_input - 9))
((b = num_bias + num_input))
((c = num_bias + num_input + 1))
((d = num_bias + num_input + num_output))
for i in `seq $a $b`; do
    for j in `seq $c $d`; do
	echo gene $trait $i $j 0.0 0 $innov 0 1 >> $file;
	((innov = innov + 1));
	((trait = trait + 1));
	if [ $trait -gt 3 ]; then
	    trait=1;
	fi;
    done;
done

# TAIL
echo genomeend 1 >> $file

