import requests
import json
import sys

# Mattermost server
source_conn_dict = {
    "url" : "http://localhost:8065",
    "username" : "traum",
    "password" : "n3hLkj8t6pana@x"
}

# Mattermost target server
target_conn_dict = {
    "url" : "http://3.89.44.182:8065",
    "username" : "admin@mattermost.com",
    "password" : "MattermostDemo,1"
}

# Global variables
files = []
message = ""

class MattermostServer:
    login_suffix = "/api/v4/users/login"
    teams_suffix = "/api/v4/teams"
    channels_suffix = "/channels"
    channel_create_suffix = "/api/v4/channels"
    __logon_header_dict = {}
    
    def __init__(self, connection_dict):
        self.url = connection_dict["url"]
        self.username = connection_dict["username"]
        self.password = connection_dict["password"]

    def login(self):
        self.login_url = self.url + self.login_suffix

        if self.login_url and self.username and self.password:
            # Mattermost user/password to import with
            payload = { "login_id": self.username,
                        "password": self.password}
        
            self.headers = {"content-type": "application/json"}
            s = requests.Session()
            r = s.post(self.login_url, data=json.dumps(payload), headers=self.headers)
            auth_token = r.headers.get("Token")
            self.__login_header_dict = {"Authorization": "Bearer " + auth_token}
        else:
            print("Please ensure that Login-URL, username and password are set.")
    
    def get_teams(self):
        teams_url = self.url + self.teams_suffix
        response = requests.get(teams_url, headers=self.__login_header_dict)
        info = response.json()
        return info
    
    def create_team(self, team_info):
        teams_url = self.url + self.teams_suffix
        
        response = requests.post(teams_url, headers=self.__login_header_dict, \
            json={ "name": team_info["name"], \
                "display_name": team_info["display_name"], \
                "type": team_info["type"] })
        info = response.json()
        return info

    def get_channels(self, team_id):
        channels_url = self.url + self.teams_suffix + "/" + team_id + self.channels_suffix
        response = requests.get(channels_url, headers=self.__login_header_dict) #, json=payload)
        info = response.json()
        return info
    
    def create_channel(self, team_id, channel_info):
        # channels_url = self.url + self.teams_suffix + "/" + team_id + self.channels_suffix
        channels_url = self.url + self.channel_create_suffix
        
        print(channels_url)
        response = requests.post(channels_url, headers=self.__login_header_dict, \
            json={ "team_id": team_id, \
                "name": channel_info["name"], \
                "display_name": channel_info["display_name"], \
                "type": channel_info["type"] })
        info = response.json()
        print(info)
        return info

def main():
    if (len(sys.argv)==2):
        if (sys.argv[1]=="show"):
            sourceServer = MattermostServer(source_conn_dict)
            sourceServer.login()
            sourceteams = sourceServer.get_teams()

            print ("SOURCE SERVER - TEAMS FOUND")
            print("TEAM COUNT - {}".format(len(sourceteams)))

            for sourceteam in sourceteams:
                print("\tTEAM INFO:")
                print("\t\tName:\t\t" + sourceteam["name"])
                print("\t\tDisplay Name:\t" + sourceteam["display_name"])
                print("\t\tAdmin Email:\t" + str(sourceteam["email"]))
                print("\t\tType:\t\t" + str(sourceteam["type"]))

                ### List channels by team
                sourcechannels = sourceServer.get_channels(sourceteam["id"])
                print("\n\t\tCHANNEL INFO:")
                for sourcechannel in sourcechannels:
                    print("\t\t\tName:\t\t" + sourcechannel["name"])
                    print("\t\t\tDisplay Name:\t" + sourcechannel["display_name"])
                    print("\t\t\tMessage Count:\t" + str(sourcechannel["total_msg_count"]))
                    print("\t\t\tType:\t\t" + str(sourcechannel["type"]))
            print("\n")
        elif(sys.argv[1]=='apply'):                    
            sourceServer = MattermostServer(source_conn_dict)
            sourceServer.login()
            sourceteams = sourceServer.get_teams()

            targetServer = MattermostServer(target_conn_dict)
            targetServer.login()
            targetteams = targetServer.get_teams()

            for sourceteam in sourceteams:
                ### List channels by team
                sourcechannels = sourceServer.get_channels(sourceteam["id"])
                target_team_id = ""

                if (sourceteam["name"] not in map(lambda t: t["name"], targetteams)):
                    print("New Team found, creating Team: {}".format(sourceteam["name"]))
                    target_team_id = targetServer.create_team(sourceteam)["team_id"]

                else:
                    print("Team {} already exists, skipping".format(sourceteam["name"]))
                    temp_target_team = next(t for t in targetteams if t["name"] == sourceteam["name"])
                    print (temp_target_team)
                    target_team_id = temp_target_team["id"]

                targetchannels = targetServer.get_channels(target_team_id)
            
                print (targetchannels)
                for sourcechannel in sourcechannels:
                    if (sourcechannel["name"] not in map(lambda c: c["name"], targetchannels)):
                        print("\tNew channel found, creating channel {}".format(sourcechannel["name"]))
                        targetServer.create_channel(target_team_id, sourcechannel)
                    else:
                        print("\tChannel {} already exists, skipping".format(sourcechannel["name"]))
        else:
            print("No matching argument found, please run the script with the argument 'show' to list data from the source server or 'apply' to create data on the target server")
            print ("e.g. 'python importer.py show'")
    else:
        print("No matching argument found, please run the script with the argument 'show' to list data from the source server or 'apply' to create data on the target server")
        print ("e.g. 'python importer.py show'")
if __name__ == "__main__":
    main()
