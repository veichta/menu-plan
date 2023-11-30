secrets:
	. secrets.sh

link:
	signal-cli link -n "cli" | tee >(xargs -L 1 qrencode -t utf8)
	
recieve:
	signal-cli -u ${SIGNAL_NUMBER} receive

mittag_menu_signal:
	python main.py | signal-cli -a ${SIGNAL_NUMBER} send --message-from-stdin -g ${SIGNAL_GROUP}

mittag_time:
	python src/time_vote.py | signal-cli -a ${SIGNAL_NUMBER} send --message-from-stdin -g ${SIGNAL_GROUP}

mittag_signal: secrets recieve mittag_menu_signal

abend_menu_signal:
	python main.py --time abend | signal-cli -a ${SIGNAL_NUMBER} send --message-from-stdin -g ${SIGNAL_GROUP}

abend_time:
	python src/time_vote.py --time abend | signal-cli -a ${SIGNAL_NUMBER} send --message-from-stdin -g ${SIGNAL_GROUP}

abend_signal: secrets recieve abend_menu_signal

