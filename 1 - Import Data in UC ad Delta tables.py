# Databricks notebook source
# MAGIC %md
# MAGIC # From JSON files to UC delta tables
# MAGIC
# MAGIC We the BloodHound dataset which refers to data collected and analyzed using the BloodHound tool, which is primarily used for mapping and identifying security vulnerabilities in Active Directory (AD) environments. 
# MAGIC For semplicity we're assuming that the data collected by the AD environments are stored into JSON files as contained into the `bloodhound` directory.
# MAGIC
# MAGIC This notebook is designed to dynamically import JSON files placed into `bloodhound` into Delta tables while ensuring that proper database constraints (primary keys and foreign keys) are enforced. These features are critical for maintaining a well-organized and efficient database that upholds data integrity and consistency.
# MAGIC
# MAGIC Once you have these constaints defined into your database you can leverage them in order to transform entity tables in nodes and foreign keys and/or join tables in relationship between nodes.

# COMMAND ----------

# MAGIC %run ./Config

# COMMAND ----------

spark.sql(f'CREATE CATALOG IF NOT EXISTS `{catalog_name}`')

# COMMAND ----------

import os

# COMMAND ----------

# Function to add foreign key constraints to a table
def add_fk(prefix: str, table_name: str, fks_dict: dict[str, dict[str, tuple[str, str]]]) -> None:
  """
  Adds a foreign key constraint to a specified table.

  Parameters:
  prefix (str): The prefix for the foreign key.
  table_name (str): The name of the table to which the foreign key constraint will be added.
  fks_dict (dict): A dictionary containing foreign key information.
  """
  fk = fks_dict[table_name]
  foreign_table_name = fk[prefix][0]
  foreing_pk = fk[prefix][1]
  spark.sql(f"""
            ALTER TABLE `{catalog_name}`.default.`{table_name}`
            ADD CONSTRAINT `{table_name}_{foreign_table_name.lower()}_{prefix}_fk`
            FOREIGN KEY({prefix}_{foreing_pk}) REFERENCES `{catalog_name}`.default.`{foreign_table_name}`
            """)

# COMMAND ----------

# List all files in the specified directory
files = dbutils.fs.ls(f'file:{os.getcwd()}/bloodhound')

# Iterate over each file and create corresponding tables
for file in files:
  table_name = file.name.replace('/', '')
  
  # Drop the table if it already exists
  spark.sql(f"DROP TABLE IF EXISTS `{catalog_name}`.default.`{table_name}`")
  
  # Create a new table from the JSON file
  spark.sql(f"""
            CREATE TABLE `{catalog_name}`.default.`{table_name}`
            AS SELECT * FROM json.`{file.path}`
            """)
  
  # Add primary key constraint if specified
  if table_name in pks:
    pk = pks[table_name]
    spark.sql(f"""
              ALTER TABLE `{catalog_name}`.default.`{table_name}`
              ALTER COLUMN {pk} SET NOT NULL
              """)
    spark.sql(f"""
              ALTER TABLE `{catalog_name}`.default.`{table_name}`
              ADD CONSTRAINT `{table_name.lower()}_pk`
              PRIMARY KEY({pk})
              """)
  # Add foreign key constraints if specified
  elif table_name in fks:
    add_fk('source', table_name, fks)
    add_fk('target', table_name, fks)
  # Raise an exception if no primary or foreign key is specified
  else:
    raise Exception(f'No primary or foreign key specified for table {table_name}')
