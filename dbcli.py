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

# Main function to handle command-line arguments
def main():
    if len(sys.argv) < 2:
        print("Usage: dbcli <goal_number> [parameters]")
        sys.exit(1)

    goal_number = int(sys.argv[1])
    driver = connect_to_db()

    # Handle different goals with appropriate functions
    if goal_number == 1:
        find_children(driver, sys.argv[2])
    elif goal_number == 2:
        count_children(driver, sys.argv[2])
    elif goal_number == 3:
        find_grandchildren(driver, sys.argv[2])
    elif goal_number == 4:
        find_parents(driver, sys.argv[2])
    elif goal_number == 5:
        count_parents(driver, sys.argv[2])
    elif goal_number == 6:
        find_grandparents(driver, sys.argv[2])
    elif goal_number == 7:
        count_unique_nodes(driver)
    elif goal_number == 8:
        find_root_node(driver)
    elif goal_number == 9:
        find_nodes_with_most_children(driver)
    elif goal_number == 10:
        find_nodes_with_least_children(driver)
    elif goal_number == 11:
        rename_node(driver, sys.argv[2], sys.argv[3])
    elif goal_number == 12:
        find_paths_between_nodes(driver, sys.argv[2], sys.argv[3])

    close_connection(driver)

# Goal 1: Finds all children of a given node
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

# Goal 2: Counts all children of a given node
def count_children(driver, node_name):
    with driver.session() as session:
        t2_start = perf_counter()
        result = session.run(
            "MATCH (parent:Category {name: $nodeName})<-[:IS_SUBCATEGORY_OF]-(child:Category) "
            "RETURN count(child) AS numberOfChildren",
            nodeName=node_name
        )
        t2_end = perf_counter()
        record = result.single()
        print(record["numberOfChildren"])
    print(t2_end - t2_start)

# Goal 3: Finds all grandchildren of a given node
def find_grandchildren(driver, node_name):
    with driver.session() as session:
        t3_start = perf_counter()
        result = session.run(
            "MATCH (grandparent:Category {name: $nodeName})<-[:IS_SUBCATEGORY_OF*2]-(grandchild:Category) "
            "RETURN grandchild.name",
            nodeName=node_name
        )
        t3_end = perf_counter()
        for record in result:
            print(record["grandchild.name"])
    print(t3_end - t3_start)

# Goal 4: Finds all parents of a given node
def find_parents(driver, node_name):
    with driver.session() as session:
        t4_start = perf_counter()
        result = session.run(
            "MATCH (child:Category {name: $nodeName})-[:IS_SUBCATEGORY_OF]->(parent:Category) "
            "RETURN parent.name",
            nodeName=node_name
        )
        t4_end = perf_counter()
        for record in result:
            print(record["parent.name"])
    print(t4_end - t4_start)

# Goal 5: Counts all parents of a given node
def count_parents(driver, node_name):
    with driver.session() as session:
        t5_start = perf_counter()
        result = session.run(
            "MATCH (child:Category {name: $nodeName})-[:IS_SUBCATEGORY_OF]->(parent:Category) "
            "RETURN count(parent) AS numberOfParents",
            nodeName=node_name
        )
        t5_end = perf_counter()
        record = result.single()
        print(record["numberOfParents"])
    print(t5_end - t5_start)

# Goal 6: Finds all grandparents of a given node
def find_grandparents(driver, node_name):
    with driver.session() as session:
        t6_start = perf_counter()
        result = session.run(
            "MATCH (grandchild:Category {name: $nodeName})-[:IS_SUBCATEGORY_OF*2]->(grandparent:Category) "
            "RETURN grandparent.name",
            nodeName=node_name
        )
        t6_end = perf_counter()
        for record in result:
            print(record["grandparent.name"])
    print(t6_end - t6_start)

# Goal 7: Counts how many uniquely named nodes there are
def count_unique_nodes(driver):
    with driver.session() as session:
        t7_start = perf_counter()
        result = session.run(
            "MATCH (c:Category) "
            "RETURN count(distinct c.name) AS uniqueNodesCount"
        )
        t7_end = perf_counter()
        record = result.single()
        print(record["uniqueNodesCount"])
    print(t7_end - t7_start)

# Goal 8: Finds a root node, one which is not a subcategory of any other node
def find_root_node(driver):
    with driver.session() as session:
        t8_start = perf_counter()
        result = session.run(
            "MATCH (root:Category) "
            "WHERE NOT (root)-[:IS_SUBCATEGORY_OF]->(:Category) "
            "RETURN root.name"
        )
        t8_end = perf_counter()
        records = list(result)
        if not records:
            print("No root node found.")
        else:
            for record in records:
                print(record["root.name"])
    print(t8_end - t8_start)

# Goal 9: Finds nodes with the most children
def find_nodes_with_most_children(driver):
    with driver.session() as session:
        t9_start = perf_counter()
        result = session.run(
            "MATCH (parent:Category)<-[:IS_SUBCATEGORY_OF]-(child:Category) "
            "RETURN parent.name, count(child) AS numberOfChildren "
            "ORDER BY numberOfChildren DESC "
            "LIMIT 10"
        )
        t9_end = perf_counter()
        for record in result:
            print(f"{record['parent.name']} has {record['numberOfChildren']} children")
    print(t9_end - t9_start)

# Goal 10: Finds nodes with the least children (number of children is greater than zero)
def find_nodes_with_least_children(driver):
    with driver.session() as session:
        t10_start = perf_counter()
        result = session.run(
            "MATCH (parent:Category)<-[:IS_SUBCATEGORY_OF]-(child:Category) "
            "WITH parent, count(child) AS numberOfChildren "
            "WHERE numberOfChildren > 0 "
            "RETURN parent.name, numberOfChildren "
            "ORDER BY numberOfChildren ASC "
            "LIMIT 10"
        )
        t10_end = perf_counter()
        for record in result:
            print(f"{record['parent.name']} has {record['numberOfChildren']} children")
    print(t10_end - t10_start)

# Goal 11: Renames a given node
def rename_node(driver, old_name, new_name):
    with driver.session() as session:
        t11_start = perf_counter()
        result = session.run(
            "MATCH (n:Category {name: $oldName}) "
            "SET n.name = $newName",
            oldName=old_name,
            newName=new_name
        )
        t11_end = perf_counter()
        print(f"Node '{old_name}' renamed to '{new_name}'")
    print(t11_end - t11_start)

# Goal 12: Finds all paths between two given nodes, with directed edges from the first to the second node
def find_paths_between_nodes(driver, start_node, end_node):
    with driver.session() as session:
        t12_start = perf_counter()
        result = session.run(
            "MATCH path = (start:Category {name: $startNode})-[:IS_SUBCATEGORY_OF*..5]-(end:Category {name: $endNode})"
            "RETURN path;",
            startNode=start_node,
            endNode=end_node
        )
        t12_end = perf_counter()
        for record in result:
            print(record["path"])
    print(t12_end - t12_start)

if __name__ == "__main__":
    main()
