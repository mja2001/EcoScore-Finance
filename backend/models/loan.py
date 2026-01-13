from datetime import datetime
from config.database import DatabaseConfig

class Loan:
    """Loan data model"""
    
    def __init__(self, loan_id, borrower_name, loan_amount, project_type, 
                 description, eco_score=None, predicted_carbon_reduction=None):
        self.loan_id = loan_id
        self.borrower_name = borrower_name
        self.loan_amount = loan_amount
        self.project_type = project_type
        self.description = description
        self.eco_score = eco_score
        self.predicted_carbon_reduction = predicted_carbon_reduction
        self.status = 'pending'
        self.created_at = datetime.now()
    
    @staticmethod
    def create(loan_data):
        """Create a new loan in the database"""
        conn = DatabaseConfig.get_postgres_connection()
        if not conn:
            return None
        
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO loans 
                (loan_id, borrower_name, loan_amount, project_type, description, 
                 eco_score, predicted_carbon_reduction, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                loan_data['loan_id'],
                loan_data['borrower_name'],
                loan_data['loan_amount'],
                loan_data['project_type'],
                loan_data['description'],
                loan_data.get('eco_score'),
                loan_data.get('predicted_carbon_reduction'),
                'pending'
            ))
            
            loan_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            conn.close()
            return loan_id
        except Exception as e:
            print(f"Error creating loan: {e}")
            conn.rollback()
            cursor.close()
            conn.close()
            return None
    
    @staticmethod
    def get_by_id(loan_id):
        """Get loan by ID"""
        conn = DatabaseConfig.get_postgres_connection()
        if not conn:
            return None
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT loan_id, borrower_name, loan_amount, project_type, 
                   description, eco_score, predicted_carbon_reduction, 
                   status, created_at
            FROM loans WHERE loan_id = %s
        """, (loan_id,))
        
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if row:
            return {
                'loan_id': row[0],
                'borrower_name': row[1],
                'loan_amount': float(row[2]),
                'project_type': row[3],
                'description': row[4],
                'eco_score': float(row[5]) if row[5] else None,
                'predicted_carbon_reduction': float(row[6]) if row[6] else None,
                'status': row[7],
                'created_at': row[8].isoformat() if row[8] else None
            }
        return None
    
    @staticmethod
    def get_all():
        """Get all loans"""
        conn = DatabaseConfig.get_postgres_connection()
        if not conn:
            return []
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT loan_id, borrower_name, loan_amount, project_type, 
                   eco_score, status, created_at
            FROM loans ORDER BY created_at DESC
        """)
        
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        loans = []
        for row in rows:
            loans.append({
                'loan_id': row[0],
                'borrower_name': row[1],
                'loan_amount': float(row[2]),
                'project_type': row[3],
                'eco_score': float(row[4]) if row[4] else None,
                'status': row[5],
                'created_at': row[6].isoformat() if row[6] else None
            })
        
        return loans
    
    @staticmethod
    def update_score(loan_id, eco_score, predicted_carbon_reduction):
        """Update loan's environmental score"""
        conn = DatabaseConfig.get_postgres_connection()
        if not conn:
            return False
        
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE loans 
                SET eco_score = %s, 
                    predicted_carbon_reduction = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE loan_id = %s
            """, (eco_score, predicted_carbon_reduction, loan_id))
            
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating score: {e}")
            conn.rollback()
            cursor.close()
            conn.close()
            return False
