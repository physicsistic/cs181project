import subprocess


for i in range(100):
	print i
	subprocess.call('python run_game_modified.py -d 0', shell=True)
	# subprocess.call('\n', shell=True)