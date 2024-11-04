import pymysql

connection = pymysql.connect(
    host="localhost",
    user="root",
    password="",
    database="divvy_db"
)

# reading and forming an SQL query in 500 rows of data
def read_batch_as_sql(file, batch_size=500):
    batch_rows = []
    for _ in range(batch_size):
        line = file.readline().strip().strip(',')
        if not line:
            break
        batch_rows.append(line)

    if batch_rows:
        insert_query = f"INSERT INTO trip_data VALUES {', '.join(batch_rows)};"
        return insert_query
    else:
        return None


def execute_sql_query(query):
    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()
    cursor.close()

file_path = "processed_trip_data_oct_2023.txt"

with open(file_path, 'r') as file:
    while True:
        insert_query = read_batch_as_sql(file)
        if insert_query is None:
            break
        execute_sql_query(insert_query)


connection.close()
