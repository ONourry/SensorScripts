import ast
import json
import os

import requests
import xmltodict


def makeRequest(xml_url):
    response = requests.get(xml_url)
    return response.content

def XmlToJSON(json_file,xml_content):
    with open(json_file, 'w') as out_file:
        json.dump(xmltodict.parse(xml_content), out_file)

def getDataDictionary(json_file):
    """Output dict format
         {im.r_c.android.clearweather: {'@id': 'im.r_c.android.clearweather', 'id': 'im.r_c.android.clearweather', 'added': '2016-06-24',
             'lastupdated': '2016-06-24', 'name': '清心天气', 'summary': 'Get weather forecasts (CN)',
             'icon': 'im.r_c.android.clearweather.2.png',
             'desc': '<p>Chinese weather information with a clean user interface.</p>', 'license': 'MIT',
             'categories': 'Internet', 'category': 'Internet', 'web': 'https://fir.im/clearweather',
             'source': 'https://github.com/richardchien/clear-weather-android',
             'tracker': 'https://github.com/richardchien/clear-weather-android/issues', 'marketversion': '1.0.0',
             'marketvercode': '2',
             'package': {'version': '1.0.0', 'versioncode': '2', 'apkname': 'im.r_c.android.clearweather_2.apk',
                         'srcname': 'im.r_c.android.clearweather_2_src.tar.gz', 'hash': {'@type': 'sha256',
                                                                                         '#text': 'cb688f2e0574029d6421f683cf8397c6563a033a251bfd8bb0e66649eeb68710'},
                         'size': '1616498', 'sdkver': '15', 'targetSdkVersion': '23', 'added': '2016-06-24',
                         'sig': 'b66eb548ab1a02386384da683021b07b', 'permissions': 'INTERNET'}},
            appname: {...},
        }
    """
    data = {}
    with open(json_file, encoding='utf-8') as json_data:
        data = json.load(json_data, strict=False)

    dict = {}
    for root, xml_content in data.items():  # root of xml tree: key is fdroid
        for key, value in xml_content.items():  # 2 keys, repo, application. Repo data and app data
            if key == "repo":
                continue
            else:
                # app data is a list of dict objects of all apps. Dictionary is easier to use
                for data in value:
                    app_name = data['id']
                    dict[app_name] = data

    return dict #{app_name:{...},app_name:{...}}


def getCountManifestRepo(data,github_token):
    valid_apps = [] #Apps that contain only a single AndroidManifest.xml file
    for app_name,dict in data.items():
        if not dict['source']:
            continue

        github = 'https://github.com/'
        source = dict['source'] #source is the github url
        if not github in source:
            continue

        source = source.replace(github,'')
        github_api = "https://api.github.com/repos/" + source + "/git/trees/master?recursive=1"
        headers = {'Authorization': 'token %s' % github_token}
        response = requests.get(github_api, headers=headers)
        print(response)
        if response.status_code == 404:
            continue

        content = response.content.decode() #content is binary
        manifests = content.count('AndroidManifest.xml')
        app = (dict['source'],manifests) #git hub url with # of manifests file
        valid_apps.append(app)

        # if manifests == 1:
        #     valid_apps.append(dict['source']) #append the github url of the app
    return valid_apps

def getNumberCommits(github_token,output_file=None,app_list = None):
    valid_apps = None
    if output_file:
        # I previously made a file with the result of getSingleManifestRepo, should add to the code later
        valid_apps_file = os.path.join(os.getcwd(),'valid_apps.txt')
        valid_apps = open(valid_apps_file).read()
        valid_apps = valid_apps.split(',')
    elif app_list:
        valid_apps = app_list

    github = 'https://github.com/'
    app_data = {}

    error_file =  os.path.join(os.getcwd(),'error_sum_commits.txt')

    for app in valid_apps:
        if app_list: #if app_list is init then it's a tuple (source,)
            app = app[0]

        owner_repo = app.replace(github,'')
        #the 'total' field of each contributor is the #commits without merge
        github_api = "https://api.github.com/repos/" + owner_repo + "/stats/contributors"

        headers = {'Authorization': 'token %s' % github_token}
        response = requests.get(github_api, headers=headers)
        print(response)
        if response.status_code == 404:
            continue

        content = response.content.decode()  # content is binary
        content = content.replace("false","'false'") #to avoid NameError exception
        try:
            content = ast.literal_eval(content) #convert to list from string, also converts inner strings to dict objects
        except ValueError as e:
            with open(error_file, 'a') as file:
                error = app + ", " + e.__str__()
                file.write(error)
                continue

        app_data[app] = 0
        for contributor in content:
            app_data[app] += contributor['total']

    print(app_data)

    if output_file:
        with open(output_file,'w') as file:
            file.write(str(app_data))

    elif app_list:
        return app_data

def main():
    github_token = "9c433aa0695dc1fffe1ad5bb53ce3456a537f070"
    json_file = os.path.join(os.getcwd(),'jsondata.json')

    if not os.path.isfile(json_file):
        xml_url = "https://f-droid.org/repo/index.xml"
        string_content = makeRequest(xml_url)
        XmlToJSON(json_file,string_content)

    data = getDataDictionary(json_file)
    print(len(data))
    #valid_apps =  getSingleManifestRepo(data,github_token)
    #print(valid_apps)

    apps_commit_file = os.path.join(os.getcwd(), 'apps_commit_number.txt')
    if not os.path.isfile(apps_commit_file):
        getNumberCommits(github_token,apps_commit_file)

    apps_commit_data = open(apps_commit_file).read()
    apps_commit_data = ast.literal_eval(apps_commit_data)

    valid_apps = { k: v for k, v in apps_commit_data.items() if v >= 500 } #at least 500 commits
    print(valid_apps)

if __name__ == "__main__":
    main()