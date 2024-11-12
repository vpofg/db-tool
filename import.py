import sys
from time import perf_counter, perf_counter_ns
from neo4j import GraphDatabase, basic_auth

# Neo4j connection details
uri = "bolt://localhost:7689"  # Default port is usually 7687
user = "neo4j"  # Replace with your username
password = "database"  # Replace with your password

# Function to initialize Neo4j driver
def connect_to_db():
    try:
        driver = GraphDatabase.driver(uri, auth=basic_auth(user, password))
        return driver
    except Exception as e:
        print(f"Failed to connect to Neo4j database: {e}")
        sys.exit(1)

# Function to close Neo4j driver
def close_connection(driver):
    driver.close()

def main():
    if len(sys.argv) < 2:
        print("Usage: dbcli <goal_number> [parameters]")
        sys.exit(1)

    driver = connect_to_db()
    close_connection(driver)


def find_children(driver, node_name):
    with driver.session() as session:
        t1_start = perf_counter()
        result = session.run(
            "CALL apoc.periodic.iterate( 'LOAD CSV FROM 'file:///path_to_file/taxonomy.csv' AS row RETURN row',"
            "'WITH row, trim(row[0]) AS parentCategory, trim(row[1]) AS childCategory"
            "WHERE parentCategory IS NOT NULL AND parentCategory <> "" "
            "AND childCategory IS NOT NULL AND childCategory <> "" "
            "MERGE (parent:Category {name: parentCategory})"
            "MERGE (child:Category {name: childCategory})"
            "MERGE (child)-[:IS_SUBCATEGORY_OF]->(parent)',"
            "{batchSize:1000, parallel:false}"""
            ");"
        )
        t1_end = perf_counter()
        for record in result:
            print(record["child.name"])
    print(t1_end - t1_start)


if __name__ == "__main__":
    main()