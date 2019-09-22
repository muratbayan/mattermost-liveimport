import requests
import json

# Mattermost server
source_conn_dict = {
    "url" : "http://localhost:8065",
    "username" : "traum",
    "password" : "n3hLkj8t6pana@x"
}

# Mattermost target server
target_conn_dict = {
    "url" : "http://54.80.123.104:8065",
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
    __logon_header_dict = {}

    # def __init__(self, url, username, password):
    #     self.url = url
    #     self.username = username
    #     self.password = password
    
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
        channels_url = self.url + self.teams_suffix + "/" + team_id + self.channels_suffix
        
        response = requests.post(channels_url, headers=self.__login_header_dict, \
            json={ "name": channel_info["name"], \
                "display_name": channel_info["display_name"], \
                "type": channel_info["type"] })
        info = response.json()
        return info

# def login(connection_dict):
#     login_url = connection_dict["url"] + "/api/v4/users/login"
#     username = connection_dict["username"]
#     password = connection_dict["password"]

#     if login_url and username and password:
#         # Mattermost user/password to import with
#         payload = { "login_id": username,
#                     "password": password}
#         print(payload)
#         print(json.dumps(payload))
#         print(login_url)
#         headers = {"content-type": "application/json"}
#         s = requests.Session()
#         r = s.post(login_url, data=json.dumps(payload), headers=headers)
#         print(r.headers)
#         auth_token = r.headers.get("Token")
#         # print(auth_token)
#         return {'Authorization': 'Bearer ' + auth_token}

#     else:
#         print("Please ensure that Login-URL, username and password are set.")
#         return {'Authorization': 'Bearer '}

def get_team_id(url, team_name):
    team_url = url+"/api/v4/teams/search"
    payload = { "term": team_name}
    response = requests.post(team_url, headers=hed, json=payload)
    info = response.json()
    global team_id
    team_id = info[0]["id"]

def get_channel_id(url, team_id, channel_name):
    team_url = url+"/api/v4/teams/"+team_id+"/channels/search"
    payload = { "term": channel_name}
    response = requests.post(team_url, headers=hed, json=payload)
    info = response.json()
    global channel_id
    channel_id = info[0]["id"]

def get_posts(channel_id):
    team_url = url+"/api/v4/channels/"+channel_id+"/posts"
    response = requests.get(team_url, headers=hed)
    info = response.json()
    for i in info['posts'].items():
        parse_post(i)

def get_username(user_id):
    login(login_url, username, password)
    team_url = url+"/api/v4/users/"+user_id
    response = requests.get(team_url, headers=hed)
    info = response.json()
    global user_name
    user_name = info['username']

def parse_post(p):
    post = (p[1])
    for k, v in post.items():
        if k == "user_id":
            get_username(v)
        if k == "file_ids":
            for fileid in v:
                print("FileId: "+fileid)
                get_uploads(fileid)
        if k == "message":
            message = v
    create_post(mm_url, message, user_name)

def create_post(mm_url, message, user_name):
    print("Creating a new post...")
    login(target_conn_dict)
    get_team_id(mm_url, mm_team_name)
    get_channel_id(mm_url, team_id, mm_channel_name)
    post_url = mm_url+"/api/v4/posts"
    #for i in files:
    #    print("New FileId: "+i)
    payload = {
        "channel_id":channel_id,
        "message":"**"+user_name+": **"+message,
        "file_ids":
            files
            ,
        "props": {
            #set these props if the username should be shown instead of the "import" user
            #"from_webhook":"true",
            #"override_username":user_name
            }
        }
    response = requests.post(post_url, headers=hed, json=payload)
    info = response.json()

def get_uploads(fileid):
    login(login_url, username, password)
    print("Getting uploads...")
    info_url = url+"/api/v4/files/" + fileid + '/info'
    response = requests.get(info_url, headers=hed)
    info = response.json()
    print("Getting file: "+info['name'])
    global filename
    filename = info['name']
    # Download the file
    file_url = url+"/api/v4/files/" + fileid
    response = requests.get(file_url, headers=hed)
    open(filename, 'wb').write(response.content)
    post_uploads(filename)

def post_uploads(filename):
    print("Uploading files...")
    login(mm_login_url, mm_username, mm_password)
    get_team_id(mm_url, mm_team_name)
    get_channel_id(mm_url, team_id, mm_channel_name)
    post_url = mm_url+"/api/v4/files?channel_id="+channel_id
    headers = {"content-type": "multipart/form-data"}
    file = {'upload_file': open(filename, 'rb')}
    response = requests.post(post_url, headers=hed, files=file)
    info = response.json()
    file_id = info['file_infos'][0]['id']
    str(file_id)
    files.append(file_id)

def main():

    print ("SOURCE SERVER - TEAMS FOUND")

    sourceServer = MattermostServer(source_conn_dict)
    sourceServer.login()
    sourceteams = sourceServer.get_teams()

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

    #     #print(team_info)
    #     if (team_info["name"] not in map(lambda t: t["name"], target_teams_info)):
    #         print("New team found!!! {}".format(team_info["name"]))
    #         create_team(target_conn_dict, team_info, target_headers)
    #     else:
    #         print("Team {} already exists, skipping".format(team_info["name"]))
    #         target_team_id = next(t for t in target_teams_info if t["name"] == team_info["name"])["id"]
    #         #print(target_team_id)
    #         target_channels_info = get_channels(target_conn_dict, target_team_id, target_headers)
            
    #         for channel_info in source_channels_info:
    #             # Get target channels to see if there are any missing to add
    #             print (channel_info)
    #             if (channel_info["name"] not in map(lambda c: c["name"], target_channels_info)):
    #                 print("\tNew channel found!!!")
    #                 print (channel_info)
    #                 #create_channel(target_conn_dict, target_team_id, channel_info, target_headers)
    #             else:
    #                 print("\tChannel {} already exists, skipping".format(channel_info["name"]))


    # source_headers = login(source_conn_dict)
    # print(source_headers)
    # source_teams_info = get_teams(source_conn_dict, source_headers)
    # print(source_teams_info)

    # target_headers = login(target_conn_dict)
    # target_teams_info = get_teams(target_conn_dict, target_headers)

    # for team_info in source_teams_info:
    #     ### List channels by team
    #     source_channels_info = get_channels(source_conn_dict, team_info["id"], source_headers)

    #     #print(team_info)
    #     if (team_info["name"] not in map(lambda t: t["name"], target_teams_info)):
    #         print("New team found!!! {}".format(team_info["name"]))
    #         create_team(target_conn_dict, team_info, target_headers)
    #     else:
    #         print("Team {} already exists, skipping".format(team_info["name"]))
    #         target_team_id = next(t for t in target_teams_info if t["name"] == team_info["name"])["id"]
    #         #print(target_team_id)
    #         target_channels_info = get_channels(target_conn_dict, target_team_id, target_headers)
            
    #         for channel_info in source_channels_info:
    #             # Get target channels to see if there are any missing to add
    #             print (channel_info)
    #             if (channel_info["name"] not in map(lambda c: c["name"], target_channels_info)):
    #                 print("\tNew channel found!!!")
    #                 print (channel_info)
    #                 #create_channel(target_conn_dict, target_team_id, channel_info, target_headers)
    #             else:
    #                 print("\tChannel {} already exists, skipping".format(channel_info["name"]))
            
    
        #create_team(team_info)
    # get_team_id(url, team_name)
    # get_channel_id(url, team_id, channel_name)
    # get_posts(channel_id)

if __name__ == "__main__":
    main()
