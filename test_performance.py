import subprocess

NUM_TESTS = 100

wins = 0
for i in range(NUM_TESTS):
    output = subprocess.check_output("python run_game.py -d 0 &", shell=True)
    output = output.split('\n')
    last_line = output[len(output) - 2]
    print last_line
    if last_line[0] == 'T':
        print "TIE"
    else:
        if last_line[7] == '2':
            wins += 1
            print "WIN"
        else:
            print "LOSS"

performance = float(wins) / NUM_TESTS
print "PERFORMANCE = " + str(performance)


