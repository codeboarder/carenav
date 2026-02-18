"""
Create Azure SQL Database Schema for CareNav Florida
======================================================
Built by Gregory Katz and Rick Weyenberg
Code is as-is, open source

Run after provisioning Azure SQL:
    python scripts/create_azure_schema.py

The schema matches the existing SQLAlchemy models in models/database.py
but uses T-SQL syntax for Azure SQL Database.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# TODO: Rick — Uncomment after installing pyodbc
#
# import pyodbc
#
# def create_schema():
#     conn_str = (
#         f"DRIVER={{ODBC Driver 18 for SQL Server}};"
#         f"SERVER={os.getenv('AZURE_SQL_SERVER')};"
#         f"DATABASE={os.getenv('AZURE_SQL_DATABASE')};"
#         f"UID={os.getenv('AZURE_SQL_USERNAME')};"
#         f"PWD={os.getenv('AZURE_SQL_PASSWORD')};"
#         f"Encrypt=yes;TrustServerCertificate=no;"
#     )
#     conn = pyodbc.connect(conn_str)
#     cursor = conn.cursor()
#
#     # The SQLAlchemy models in models/database.py define these tables:
#     # users, patients, care_needs, veteran_status, financials, gifts,
#     # documents, tasks, facilities, facility_matches, conversations,
#     # agent_outputs, bills, income_phases, benefit_applications,
#     # contacts, assets, medical_info, diagnoses, medications,
#     # insurance, selected_facilities
#     #
#     # Rick: Use SQLAlchemy's create_all() with the Azure SQL engine
#     # instead of raw SQL. Just swap the engine URL in database.py
#     # and run: await init_db()
#
#     print("Schema created successfully")
#     conn.close()
#
#
# if __name__ == "__main__":
#     create_schema()

print("TODO: Uncomment after installing pyodbc")
print("pip install pyodbc aioodbc")
print("")
print("Recommended approach: Just swap the engine URL in database.py")
print("and let SQLAlchemy's create_all() handle schema creation.")
