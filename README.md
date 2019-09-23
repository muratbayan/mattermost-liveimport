# mattermost-liveimport
This tools helps to import Teams/Channels from one Mattermost server to another.
Requires the Python requests module which can be installed by running 'pip install requests' from a terminal 

How to use:
1. Edit the "source_conn_dict" and "target_conn_dict" variables in importer.py to match your source and target Mattermost servers.
2. Run importer.py from a command line with one of the following options
  - 'show' to list all the Teams and Channels of the source server
  - 'apply' to go through the Teams and Channels of the source server and create them if not already there on the target server
  - e.g. 'python importer.py show'
