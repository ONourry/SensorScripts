import Crawler as crawler
import psycopg2 as psycopg2
import os
import ast

connection = None
cursor = None
try:
    connection = psycopg2.connect(user=os.environ.get('POSTGRES_REFACTORING_USER'),
                                  password=os.environ.get('POSTGRES_REFACTORING_PW'),
                                  host="127.0.0.1",
                                  port="5432",
                                  database="EnergyConsumption")
    cursor = connection.cursor()
    # Print PostgreSQL Connection properties
    print(connection.get_dsn_parameters(), "\n")

    # Print PostgreSQL version
    cursor.execute("SELECT version();")
    record = cursor.fetchone()
    print("You are connected to - ", record, "\n")

except (Exception) as error:
    print("Error while connecting to PostgreSQL", error)


def insert_app_data(data):
    for app_name,app_data in data.items():
        query = None

        apkname = None
        if type(app_data['package']) is list:
            apkname = app_data['package'][0]['apkname']
        elif type(app_data['package']) is dict:
            apkname = app_data['package']['apkname']

        if app_data['summary']:
            app_data['summary'] = app_data['summary'].replace("\'",'')

        query = """INSERT INTO public.app_data(
        app_name, date_added, license, categories, source, tracker, market_version, market_version_code,
        apk_name, summary)VALUES (\'{name}\', \'{date}\', \'{license}\',
        \'{categories}\',\'{source}\',\'{tracker}\', \'{market_ver}\', {market_ver_code}, \'{apk_name}\',
        \'{summary}\');""".format(
        name=app_name, date=app_data['added'], license=app_data['license'],
        categories=app_data['categories'], source=app_data['source'], tracker=app_data['tracker'],
        market_ver=app_data['marketversion'] , market_ver_code=int(app_data['marketvercode']),
        apk_name=apkname, summary=app_data['summary'])

        cursor.execute(query)

    connection.commit()  # Only commit at the end to speed it up


#update the rows to add the # of manifest files and # of commits in each app
def update_manifest_count(data,github_token):
    apps_manifest = crawler.getCountManifestRepo(data,github_token) #[(github url,#manifests),(x,y),...]
    print(apps_manifest) #in case something crashes in the loop to avoid sending all the req to github api again

    for tuple in apps_manifest:
        query = """UPDATE public.app_data SET android_manifests_count={count} WHERE source=\'{source}\';""".format(
            count=tuple[1],source=tuple[0]
        )

        cursor.execute(query)

    connection.commit()


def update_commit_count(github_token):
    cursor.execute("SELECT source FROM app_data WHERE source like '%github.com%'; ")
    apps = cursor.fetchall()# tuple (source,)

    app_commits = crawler.getNumberCommits(github_token=github_token,app_list=apps)

    for source,commits in app_commits.items():
        query = """UPDATE public.app_data SET commits={count} WHERE source=\'{source}\';""".format(
            count=commits, source=source
        )

        cursor.execute(query)

    connection.commit()

def main():
    github_token = "9c433aa0695dc1fffe1ad5bb53ce3456a537f070"
    app_data_file = os.path.join(os.getcwd(), 'jsondata.json')
    data = crawler.getDataDictionary(app_data_file)  # dict of app data -> see Crawler.py

    #insert_app_data(data)

    #update_manifest_count(data,github_token)

    #update_commit_count(github_token)

    connection.close()


if __name__ == "__main__":
    main()

