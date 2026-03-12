import psycopg2
from psycopg2.extras import DictCursor
import sys

# Hardcoded for migration task
OLD_DB_URL = "postgresql://ranga:lQHuZjjAtYduMoYuAL6FSHTsBd75u3Qd@dpg-d58jgkogjchc73a744k0-a.virginia-postgres.render.com/ai_receptionist_3gp5?sslmode=require"
NEW_DB_URL = "postgresql://ranga:04ZD9k3P7DJhl0IWjVofErqi2cuSMFbU@dpg-d6pgod15pdvs73a7r6t0-a.oregon-postgres.render.com/ai_receptionist_ndru?sslmode=require"

def migrate_doctors():
    print("Starting migration of doctors data...")
    
    try:
        # Connect to old DB
        print("Connecting to old database...")
        old_conn = psycopg2.connect(OLD_DB_URL)
        old_cursor = old_conn.cursor(cursor_factory=DictCursor)
        
        # Connect to new DB
        print("Connecting to new database...")
        new_conn = psycopg2.connect(NEW_DB_URL)
        new_cursor = new_conn.cursor()
        
        # Fetch all doctors from old DB
        print("Fetching doctors from old database...")
        old_cursor.execute("SELECT * FROM doctors")
        doctors = old_cursor.fetchall()
        
        if not doctors:
            print("No doctors found in the old database.")
            return 0
            
        print(f"Found {len(doctors)} doctors. Migrating to new database...")
        
        # Insert doctors into new DB
        insert_query = """
        INSERT INTO doctors (
            id, name, email, department, specialization, experience, 
            phone, bio, is_active, created_at, updated_at
        ) VALUES (
            %s, %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s
        ) ON CONFLICT (id) DO UPDATE SET
            name = EXCLUDED.name,
            email = EXCLUDED.email,
            department = EXCLUDED.department,
            specialization = EXCLUDED.specialization,
            experience = EXCLUDED.experience,
            phone = EXCLUDED.phone,
            bio = EXCLUDED.bio,
            is_active = EXCLUDED.is_active,
            updated_at = EXCLUDED.updated_at;
        """
        
        success_count = 0
        for doc in doctors:
            try:
                new_cursor.execute(insert_query, (
                    doc['id'], doc['name'], doc['email'], doc['department'], 
                    doc['specialization'], doc['experience'], doc['phone'], 
                    doc['bio'], doc['is_active'], doc['created_at'], doc['updated_at']
                ))
                new_conn.commit()
                success_count += 1
            except Exception as row_error:
                print(f"Error migrating doctor {doc['id']}: {row_error}")
                new_conn.rollback()
        
        print(f"\nMigration successfully completed! Migrated {success_count}/{len(doctors)} doctors.")

        # Let's also check if departments table exists and has the departments
        # Because doctors.department might be a foreign key or just string index.
        # In models.py we saw Department table.
        
    except psycopg2.Error as e:
        print(f"Database error occurred: {e}")
        return 1
    finally:
        if 'old_cursor' in locals(): old_cursor.close()
        if 'old_conn' in locals(): old_conn.close()
        if 'new_cursor' in locals(): new_cursor.close()
        if 'new_conn' in locals(): new_conn.close()

    return 0

if __name__ == "__main__":
    sys.exit(migrate_doctors())
