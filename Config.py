# Databricks notebook source
# MAGIC %md
# MAGIC # Content
# MAGIC
# MAGIC This notebook defines dictionaries for unique keys (uks), primary keys (pks), and foreign keys (fks) for various entities such as Computer, Domain, GPO, Group, OU, and User. It also generates lists of node tables and relationship tables based on these keys.

# COMMAND ----------

uks = {
  'Computer': 'name',
  'Domain': 'name',
  'GPO': 'name',
  'Group': 'name',
  'OU': 'name',
  'User': 'name',
}
pks = {
  'Computer': 'objectid',
  'Domain': 'objectid',
  'GPO': 'objectid',
  'Group': 'objectid',
  'OU': 'objectid',
  'User': 'objectid',
}
fks = {
  'Group-ADMIN_TO-Computer': {'source': ('Group', 'objectid'), 'target': ('Computer', 'objectid')},
  'User-ALLOWED_TO_DELEGATE-Computer': {'source': ('User', 'objectid'), 'target': ('Computer', 'objectid')},
  'User-CAN_RDP-Computer': {'source': ('User', 'objectid'), 'target': ('Computer', 'objectid')},
  'Group-CAN_RDP-Computer': {'source': ('Group', 'objectid'), 'target': ('Computer', 'objectid')},
  'Domain-CONTAINS-OU': {'source': ('Domain', 'objectid'), 'target': ('OU', 'objectid')},
  'OU-CONTAINS-Computer': {'source': ('OU', 'objectid'), 'target': ('Computer', 'objectid')},
  'OU-CONTAINS-User': {'source': ('OU', 'objectid'), 'target': ('User', 'objectid')},
  'Group-DC_SYNC-Domain': {'source': ('Group', 'objectid'), 'target': ('Domain', 'objectid')},
  'User-EXECUTE_DCOM-Computer': {'source': ('User', 'objectid'), 'target': ('Computer', 'objectid')},
  'Group-EXECUTE_DCOM-Computer': {'source': ('Group', 'objectid'), 'target': ('Computer', 'objectid')},
  'Group-GENERIC_ALL-Domain': {'source': ('Group', 'objectid'), 'target': ('Domain', 'objectid')},
  'Group-GENERIC_ALL-Computer': {'source': ('Group', 'objectid'), 'target': ('Computer', 'objectid')},
  'Group-GENERIC_ALL-User': {'source': ('Group', 'objectid'), 'target': ('User', 'objectid')},
  'Group-GENERIC_ALL-Group': {'source': ('Group', 'objectid'), 'target': ('Group', 'objectid')},
  'Group-GENERIC_WRITE-User': {'source': ('Group', 'objectid'), 'target': ('User', 'objectid')},
  'Group-GENERIC_WRITE-GPO': {'source': ('Group', 'objectid'), 'target': ('GPO', 'objectid')},
  'Group-GET_CHANGES-Domain': {'source': ('Group', 'objectid'), 'target': ('Domain', 'objectid')},
  'Group-GET_CHANGES_ALL-Domain': {'source': ('Group', 'objectid'), 'target': ('Domain', 'objectid')},
  'GPO-GP_LINK-Domain': {'source': ('GPO', 'objectid'), 'target': ('Domain', 'objectid')},
  'GPO-GP_LINK-OU': {'source': ('GPO', 'objectid'), 'target': ('OU', 'objectid')},
  'Domain-GP_LINK-OU': {'source': ('Domain', 'objectid'), 'target': ('OU', 'objectid')},
  'Computer-HAS_SESSION-User': {'source': ('Computer', 'objectid'), 'target': ('User', 'objectid')},
  'Computer-MEMBER_OF-Group': {'source': ('Computer', 'objectid'), 'target': ('Group', 'objectid')},
  'User-MEMBER_OF-Group': {'source': ('User', 'objectid'), 'target': ('Group', 'objectid')},
  'Group-MEMBER_OF-Group': {'source': ('Group', 'objectid'), 'target': ('Group', 'objectid')},
  'Group-OWNS-Domain': {'source': ('Group', 'objectid'), 'target': ('Domain', 'objectid')},
  'Group-WRITE_DACL-Domain': {'source': ('Group', 'objectid'), 'target': ('Domain', 'objectid')},
  'Group-WRITE_OWNER-Domain': {'source': ('Group', 'objectid'), 'target': ('Domain', 'objectid')},
}

# COMMAND ----------

node_tables = [key.lower() for key in pks.keys()]
rel_tables = [key.lower() for key in fks.keys()]

# COMMAND ----------

catalog_name = "dbx_genai_bloodhound_demo"
