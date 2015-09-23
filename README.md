# turfstats
Command line programs for monitoring your activity in the game Turf

Usage:

1. Install Python. Make sure you have at least version 2.4.2 of the requests module. "pip install requests" should do it, or sudo apt-get install python-requests on Linux.

2. Copy the file "sample_turf_config.txt" to "turf_config.txt" in place and edit it to add your data (username and home location). The latter is optional and not very useful until you're monitoring lots of zones.

3. Try running "turf.py". It should say how many zones you have and how long you've had them for.

4. Add a cron job / scheduled task to run "get_turf_data.py" at intervals, say every 20 minutes. A sample crontab file is provided in crontab.sample : on Linux you can just add in your paths and run with this. It also installs jobs to run once a month on the first Sunday when turf rolls over: it basically backs up the data and the leader board and wipes the data file.

5. This will then notice when you take zones and add them to the monitoring, and build up a picture of the expected return from taking each zone. This data can then be viewed by running "turf_report.py". By default it shows data for all users, with the "-u" flag it can show just your data (timeline) also. See usage for further options.

6. There are various other experimental scripts that are currently self-documenting...
