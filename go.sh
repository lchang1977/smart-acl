interval=5
total=30
samples=$(($total/$interval))
i=1
unset IFS # restore IFS to default

for i in $(seq "$samples"); do
	bandwidth=$(python -S -c "import random; print random.randrange(20000000,40000000)")
	bm=$((bandwidth / 1024 / 1024))
	tput setaf 2; echo "$i) generating background traffic at $bm/mbps"; tput sgr0
	timeout 5 wget -qO- http://10.0.0.6/sample.bin --limit-rate=$bandwidth &> /dev/null
done
