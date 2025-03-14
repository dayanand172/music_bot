import subprocess

# Start both bots as separate processes
bot1 = subprocess.Popen(["python", "listen2play_bot.py"])
bot2 = subprocess.Popen(["python", "melody4stream_bot.py"])

# Keep the script running
bot1.wait()
bot2.wait()