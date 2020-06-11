import os
import subprocess
import sys
import psycopg2 as psycopg2

cursor=None
connection=None
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


def setup_env():
    subprocess.call(["export","JAVA_HOME=/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.242.b08-0.el7_7.x86_64/jre"])
    subprocess.call(["export", "PATH=$JAVA_HOME/bin:$PATH"])


def cdRMDir(rm_dir):
    subprocess.call(["cd",rm_dir])


def generateRMExec():
    #subprocess.call(["git","clone","https://github.com/ONourry/RefactoringMiner.git"])
    #subprocess.call(["cd","RefactoringMiner"])
    subprocess.call(["./gradlew","distZip",
                     "-Dorg.gradle.java.home=\"/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.242.b08-0.el7_7.x86_64/jre\""])
    subprocess.call(["cd","build/distributions"])
    subprocess.call(["unzip","RefactoringMiner-1.0.zip"])
    subprocess.call(["cd","RefactoringMiner-1.0/bin"])


def getProjectList(list_id):
    projects = None
    filepath = os.getcwd()
    if list_id == 1:
        filepath = os.path.join(filepath,"list1.txt")
    elif list_id == 2:
        filepath = os.path.join(filepath,"list2.txt")
    elif list_id == 3:
        filepath = os.path.join(filepath,"list3.txt")
    elif list_id == 4:
        filepath = os.path.join(filepath,"list4.txt")

    with open(filepath) as file:
        projects=file.read()
        projects = projects.split("\n")

    return projects


def cloneRepo(repo_dir,github_url):
    clone_process = subprocess.Popen(["git", "clone",github_url],stdout=subprocess.PIPE,cwd=repo_dir)
    output = clone_process.communicate()[0]

#./RefactoringMiner -a /home/oliviern/RefactoringProject/cloned_projects/jdt_core/eclipse.jdt.core master > jdt_core_output.json
def runRM(project_path,rm_dir):
    rm_process = subprocess.Popen(["./RefactoringMiner","-a",project_path,"master"],
                                  stdout=subprocess.PIPE,cwd=rm_dir)
    output = rm_process.communicate()[0]


def deleteRepoClone(projectName,repo_dir):
    subprocess.Popen(["rm","-rf",projectName],stdout=subprocess.PIPE,cwd=repo_dir)



def update_rm_column(source):
    query = """UPDATE public.app_data SET rm_executed={executed} WHERE source=\'{source}\';""".format(
        executed=1, source=source)
    print(query)

    cursor.execute(query)


    connection.commit()


def main():
    rm_dir = "/home/olivier/RefactoringMiner/build/distributions/RefactoringMiner-1.0/bin"
    repo_clone_dir = "/home/olivier/clone_dir"
    output_dir = "/home/olivier/output"

    list_id = sys.argv[1]
    #setup_env()
    #generateRMExec()

    project_list = getProjectList(list_id)

    for project in project_list:
        cloneRepo(repo_clone_dir,project)

        projectName = project.split("/")[-1]
        project_path = os.path.join(repo_clone_dir,projectName)
        runRM(project_path,rm_dir)

        deleteRepoClone(projectName,repo_clone_dir)

        update_rm_column(project)

    connection.close()

if __name__ == "__main__":
    main()

#DEFAULT_JVM_OPTS="-Xms256m -Xmx16g"
#-Xms256m -Xmx16g

