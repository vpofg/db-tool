# DB2 14 Michał Konieczny Jan Gwara

## The Tech Stack

For the following project we have chosen a basic but effective stack of technology. 

### DB management

For the database management we have chosen neo4j due to the following factors:
- Extensive plugin library (APOC was used)
- Updated documentation
- Scalability (operations with over 5 million entries in CSV and over 2 million nodes in graph)
- Flexibility (self-hosted, real-time updates)
- Cypher Language

### DB command-line tool

To prepare the database command-line tools, we used python with neo4j library imported.

We have chosen python due to its simplicity and versatility. By implementing the neo4j library in the script, it's possible to interact with the database.

### Hardware
It is important to note that the whole project was made on a MacBook Pro with M1 Pro ARM architecture with macOS Sonoma 14.2.1. Results may vary for different systems, but the code was optimized for unix-like systems.


## Architecture
The main component of the project is the database. The command line tool in python interacts with the database through the neo4j library. 

</br>

## Prerequisites
To ensure proper and fast setup and configuration the user should have the following ready:
</br>

**Software modules:**  Python 3.11+, pip3, JDK17

**Database:**  neo4j 20.0.0 + 

**Other Requirements:** APOC plugin, chrome web browser, taxonomy.csv file, 2GB of free disk space

The above is the set of software the user is required to obtain prior to setup.

</br>

## Installation and Setup

After installing all software from Prerequisites chapter perform the following steps.

</br> 

To clone the repository to the desired folder use:

```
git clone https://gitlab.kis.agh.edu.pl/databases-2-2024/db2-14-michal-konieczny-jan-gwara
```
From here on now, the directory for the python scripts is the one created with clone
</br>

### Preparing DB environment
First it is needed to allocate the installed APOC plugin in the neo4j directory. It is necessary that the ```.jar``` file is located in the ```$NEO4J_HOME\plugin``` directory

</br>

Next the ```.csv``` file containing all the data, needs to be put in the ```$NEO4J_HOME\import``` directory to access it later.

</br>

### Preparing the CLI environment
With python, pip and neo4j library installed navigate to the directory where the```dbcli.py``` file is located and use the command: 

</br>

```bash
python3 dbcli <task_number> <"node_name"> <"node_name_optional">
```

</br>
To run the tool.
</br> 
</br> 

>Important note: Please ensure that in the python script uri, username and password math the ones defined by the user. The default port for bolt connection is 7687, but it is possible that a user has a service already running on that port

</br>

## User Manual
In order to ensure proper run of the app, in the command line on your PC direct to the neo4j directory (defined during installation) and from there:
</br>
</br>
To run the console:

```
$NEO4J_HOME\bin\neo4j console
```

and to run as background service:

```
$NEO4J_HOME\bin\neo4j start
```
Where ```$NEO4J_HOME``` is the downloaded neo4j package.

We recommend running neo4j as a console in order not to overuse resources on the users PC. 

After the console is started, in the web browser of your choice (preferably google chrome) go to: ```http://localhost:7474```. You will be greeted with a dashboard for queries. The default username and password are both ```neo4j```. Change the password to ```database```. Now the project is setup and ready to be used.
</br>

As the project runs locally, the user has to populate the database with data themselves by employing two queries. First we have to upload the contents of the CSV file into the database. To do that the user has to place the correct path to the import directory of neo4j and run the following query:

````SQL
CALL apoc.periodic.iterate(
'LOAD CSV FROM "file:///path_to_import_directory/taxonomy.csv" AS row RETURN row',
'WITH row, trim(row[0]) AS parentCategory, trim(row[1]) AS childCategory
WHERE parentCategory IS NOT NULL AND parentCategory <> "" AND childCategory IS NOT NULL AND childCategory <> ""
MERGE (parent:Category {name: parentCategory})
MERGE (child:Category {name: childCategory})
MERGE (child)-[:IS_SUBCATEGORY_OF]->(parent)',
{batchSize:1000, parallel:false}
);
````

</br> 

The process of filling the database should take around one minute and when its done you will see the message that around 5 million nodes where created.
</br> 

If everything went correctly, it is possible to start using the dbcli tool. To use it, refer to **"Preparing the CLI environment"** in **"Installation and Setup**

</br> 

An alternative way is to use the ```import.py``` script, but the user still has to correct the path in the file.

</br> 

## Design and Implementation 

### DB design
The database was designed on a simple premise based on the structure of the CSV file. The file is constructed in a way that each line represents a link between two nodes, where the first entry is the parent and the second is the child. We have decided to connect the nodes through ```IS_SUBCATEGORY_OF``` relationship. Each node in the dataset has a property *name*.The relationship looks as follows:

</br> 

```
(child)-[:IS_SUBCATEGORY_OF]->(parent)
```

</br> 
</br> 

The import query is created using ```APOC``` plugin of neo4j to make use of the periodic iterate function which breaks the file import into smaller chunks which improves efficiency. 

</br> 
</br> 

Then each entry is assigned a parent or child category following the pattern of the CSV ```"parent_node", "child_node"``` With the import done, we could go to creating queries for the 12 tasks.

</br> 

### Query Design
In order to navigate through the data we had to create queries that solve 12 of the problems.

</br> 

#### Finds all children of a given node

```
MATCH (parent:Category {name: $nodeName})<-[:IS_SUBCATEGORY_OF]-(child:Category)
RETURN child.name AS ChildName;
```

#### Counts all children of a given node

```
MATCH (parent:Category {name: $nodeName})<-[:IS_SUBCATEGORY_OF]-(child:Category)
RETURN count(child) AS numberOfChildren;
```

#### Finds all grand children of a given node

```
MATCH (grandparent:Category {name: $nodeName})<-[:IS_SUBCATEGORY_OF*2]-(grandchild:Category)
RETURN grandchild.name;
```

#### Finds all parents of a given node 

```
MATCH (child:Category {name: $nodeName})-[:IS_SUBCATEGORY_OF]->(parent:Category)
RETURN parent.name;
```

#### Counts all parents of a given node

```
MATCH (child:Category {name: $nodeName})-[:IS_SUBCATEGORY_OF]->(parent:Category)
RETURN count(parent) AS numberOfParents;
```

#### Finds all grand parents of a given node

```
MATCH (grandchild:Category {name: $nodeName})-[:IS_SUBCATEGORY_OF*2]->(grandparent:Category)
RETURN grandparent.name;
```

#### Counts how many uniquely named nodes there are

```
MATCH (c:Category)
RETURN count(distinct c.name) AS uniqueNodesCount;
```

#### Finds a root node, one which is not a subcategory of any other node

```
MATCH (root:Category)
WHERE NOT (root)-[:IS_SUBCATEGORY_OF]->(:Category)
RETURN root.name;
```

#### Finds nodes with the most children, there could be more the one

```
MATCH (parent:Category)<-[:IS_SUBCATEGORY_OF]-(child:Category)
RETURN parent.name, count(child) AS numberOfChildren
ORDER BY numberOfChildren DESC
LIMIT 10;
```

#### Finds nodes with the least children (number of children is greater than zero), there could be more the one

```
MATCH (parent:Category)<-[:IS_SUBCATEGORY_OF]-(child:Category)
WITH parent, count(child) AS numberOfChildren
WHERE numberOfChildren > 0
RETURN parent.name, numberOfChildren
ORDER BY numberOfChildren ASC
LIMIT 10;
```

#### Renames a given node

```
MATCH (n:Category {name: $oldName})
SET n.name = $newName;
```

#### Finds all paths between two given nodes, with directed edges from the first to the second node

```
MATCH path = (start:Category {name: $startNode})-[:IS_SUBCATEGORY_OF*]-(end:Category {name: $endNode})
RETURN path;
```

### DB command-line tool design
The command-line tool was created in python using the neo4j library in python in order to ensure connection to the DB and run queries.
</br> </br> 

>Important Note: To use the dbcli, neo4j client has to be running as in **User Manual**

</br> 
Each task has its own function defined which takes in appropriate number of arguments and runs the query in the DB and later displays the result to the user.
</br> 
</br>
Each query is surrounded by timestamps using  ```per_counter()``` function
</br> 
</br>

```python
def find_children(driver, node_name):
    with driver.session() as session:
        t1_start = perf_counter()
        result = session.run(
            "MATCH (parent:Category {name: $nodeName})<-[:IS_SUBCATEGORY_OF]-(child:Category) "
            "RETURN child.name",
            nodeName=node_name
        )
        t1_end = perf_counter()
        for record in result:
            print(record["child.name"])
    print(t1_end - t1_start)
```

We can observe that when the session is connected, the query is executed and two timestamps are created before and after execution and then subtracted to print the outcome. The perf_counter() function measures the performance of the program not relying on wall-clock time but on the  high-resolution timers such as CPU timestamp counter. 
</br>
</br>
For improving the efficiency, a simple indexing was implemented 

```
CREATE INDEX FOR (c:Category) ON (c.name);
```

The above, improves search by name, which is the most common in all the designed queries.
</br>
</br>
## Parts

- Setting up the database 
- Designing the query for data upload
	- The query was created and uploaded, there were many versions of the query as working with a big data model like this one was demanding for the system.
- First 6 queries 
- Documentation
- Designing last 6 queries
- Designing the python script
	- The script had to be implemented in a way that the command in terminal takes in predefined values and uses appropriate function. The program also takes note and calculates time of execution.
- Help with documentation
- Final presentation

## Reproducing the results

By following the instructions closely, any user should obtain similar results, altough it is worthy to note that the computer hardware might influence the times of execution.
</br> 

If all of the previous steps from **Installation and Setup** and **User Manual** where reproduced corectly the user should be able to use the dbcli tool on the database. To recap:

1. Connect to the DB
    1. Direct to ```$NEO4J_HOME\bin\neo4j console``` or ```$NEO4J_HOME\bin\neo4j start``` to initialize the DB service
    2. Go to ```http://localhost:7474```
    3. Enter the credentials ```bolt://localhost7687``` user: ```neo4j``` password: ```neo4j``` (has to be changed to database)
2. Apply the import query defined in **User Manual**
3. Initialize dbcli tool
    1. In the terminal/cmd direct to the directory where ```dbcli.py``` file is located
    2. to use the tool write ```python3 dbcli.py ex_number "argument_1" "argument_2"```

## Results

Below are the result of running each query and checking the times with the ```perf_counter()``` function.

| Query Number | T1 (in ms) | T2    | T3    |
|--------------|------------|-------|-------|
| 1            | 19.02      | 32.24 | 13.28 |
| 2            | 19.12      | 12.38 | 14.64 |
| 3            | 80.44      | 28.81 | 13.61 |
| 4            | 68.82      | 13.52 | 12.56 |
| 5            | 54.04      | 10.93 | 11.28 |
| 6            | 58.18      | 13.86 | 12.49 |
| 7            | 60.45      | 18.35 | 11.20 |
| 8            | 87.42      | 11.69 | 16.10 |
| 9            | 13.11      | 17.10 | 15.38 |
| 10           | 11.91      | 11.65 | 10.28 |
| 11           | 164.22     | 21.60 | 10.71 |
| 12           | 63.53      | 9.12  | 7.26  |

For each task the node **"1880s_films"** was used, for $11^{th}$ we have used **"ALbums_by_artist"** and changed the name to **"Albums_by_artists"** and for $12^{th}$ we have used **"1880s_films"** and **"1889_films"**.


## Self-Evaluation

### Choice of Technology

The tech stakc chosen was relativelly basic, but has offered a stable way to manage the database. The biggest issue we had was with the csv loading query. We have started with just a simple one line query using ```LOAD CSV FROM``` and we gradualy made improvements to accomodate for such a grand dataset. We have ended up with time of around 192 ms for starting streaming 1 record and around 62204 ms for completing the whole operation.

</br>
The choice of python was relatively easy, as it is an easy to develop language for scripts and also works on most machines. Being non-compiler based also helped with deployment of the tool.

### Queries

The queries designed where easy for the most part. We have had some trobles with query number 9, as we did not know how to accomodate for possily multiple nodes with the same amount of children. It was a problem we did not manage to fix and right now the query does display 10 of the biggest queries but we cannot be sure that it doesn't loose some nodes. 

### Speeds

The upload speed is rather in the middle ground. 6 minutes is rather a very average time for workig with a dataset of this size. When it comes to query execution, the times vary for each run and depending on the node we are working with in each task.


## Future expansion

The project is surely lacking in some spaces and we belive that it could be imporved by introducing some changes and extensions.

</br>
One idea to expand would be hosting the database in the cloud and minimizing the need for user interference also some scripts could be more automated.

</br>
Also some of the queires could be improved to accomodate for some outliers in the data, or extrodinary events such as query number 9.# db-tool
