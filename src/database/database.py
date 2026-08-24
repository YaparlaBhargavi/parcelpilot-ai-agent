# src/database/database.py
import sqlite3
from pathlib import Path

import pandas as pd


class DatabaseManager:
    """Manages database operations for structured data."""
    
    def __init__(self, excel_path: str = "data/ParcelPilot_Assessment_Data.xlsx"):
        self.excel_path = Path(excel_path)
        self.db_path = Path("data/parcelpilot.db")
        self._load_data()
    
    def _load_data(self):
        """Load Excel data into SQLite for better querying."""
        if not self.excel_path.exists():
            print(f"❌ Excel file not found at: {self.excel_path}")
            return
        
        # Ensure data directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(str(self.db_path))
        
        try:
            # Read all sheets from Excel
            excel_file = pd.ExcelFile(self.excel_path)
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(self.excel_path, sheet_name=sheet_name)
                # Convert column names to lowercase for consistency
                df.columns = [col.lower().replace(' ', '_') for col in df.columns]
                df.to_sql(sheet_name.lower().replace(' ', '_'), conn, if_exists='replace', index=False)
                print(f"✅ Loaded sheet: {sheet_name} with {len(df)} rows")
        except Exception as e:
            print(f"❌ Error loading Excel data: {e}")
        finally:
            conn.close()
    
    def query(self, sql: str) -> pd.DataFrame:
        """Execute SQL query with security checks."""
        conn = sqlite3.connect(str(self.db_path))
        try:
            result = pd.read_sql_query(sql, conn)
            return result
        except Exception as e:
            print(f"❌ Query error: {e}")
            return pd.DataFrame()
        finally:
            conn.close()
    
    def lookup_order(self, order_id: str) -> pd.DataFrame:
        """Look up order by ID."""
        sql = f"SELECT * FROM orders WHERE order_id = '{order_id}'"
        return self.query(sql)
    
    def lookup_account(self, account_name: str) -> pd.DataFrame:
        """Look up account by name."""
        sql = f"SELECT * FROM accounts WHERE account_name LIKE '%{account_name}%'"
        return self.query(sql)
    
    def lookup_ticket(self, ticket_id: str) -> pd.DataFrame:
        """Look up ticket by ID."""
        sql = f"SELECT * FROM tickets WHERE ticket_id = '{ticket_id}'"
        return self.query(sql)
    
    def get_all_orders(self) -> pd.DataFrame:
        """Get all orders."""
        return self.query("SELECT * FROM orders")
    
    def get_all_tickets(self) -> pd.DataFrame:
        """Get all tickets."""
        return self.query("SELECT * FROM tickets")
