#ready


import os
import json
import pyodbc
import time
from datetime import datetime, timedelta

def get_interval_from_db():
    try:
        conn = pyodbc.connect(
            "DRIVER={SQL Server};"
            "SERVER=**;"
            "DATABASE=tooshar;"
            "UID=**;"
            "PWD=**"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT TOP 1 interval_seconds FROM AOI_Config ORDER BY id DESC")
        row = cursor.fetchone()
        conn.close()

        if row and row[0] is not None:
            return int(row[0])
        else:
            print("[WARNING] No interval found in DB. Using default 1800 seconds.")
            return 1800
    except Exception as e:
        print(f"[ERROR] Failed to fetch interval from DB: {e}")
        return 1800

def main(interval_seconds):
    # Cutoff time based on DB interval
    LOG_DIR = "\\\\172.19.0.125\\aoi\\databackup"
    interval_seconds = get_interval_from_db()
    conn = pyodbc.connect(
        "DRIVER={SQL Server};"
        "SERVER=**;"
        "DATABASE=tooshar;"
        "UID=**;"
        "PWD=**"
    )
    cursor = conn.cursor()

    cursor.execute("SELECT MAX(exe_end_time) FROM AOI_CONFIG")  
    last_end_time = cursor.fetchone()[0]

    if last_end_time:
        cutoff_time = last_end_time
    else:
        cutoff_time = datetime.now() - timedelta(seconds=interval_seconds)

    exe_start_time=datetime.now()
    
    start_date = cutoff_time.date()
    end_date = datetime.now().date()

    while start_date <= end_date:
        folder_name = start_date.strftime('%Y%m%d')
        folder_path = os.path.join(LOG_DIR, folder_name)

        if not os.path.exists(folder_path):
            start_date += timedelta(days=1)
            continue

        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith((".txt", ".json")):
                    full_path = os.path.join(root, file)
                    file_time = datetime.fromtimestamp(os.path.getmtime(full_path))
                    if start_date==cutoff_time.date() and file_time < cutoff_time:
                        continue

                    with open(full_path, 'r') as f:
                        try:
                            content = json.load(f)
                        except Exception as e:
                            print(f"Skipping {file} due to invalid JSON: {e}")
                            continue

                    barcode = content.get("barcode")
                    machine = content.get("machine")
                    result = content.get("result")
                    entries = content.get("data", [])

                    ALLOWED_ERROR_CODES = {"Missing", "Wrong Polarity", "UpSideDown", "Bridge"}

                    for item in entries:
                        entry_id = item.get("id")
                        error_flag = item.get("errorFlag")
                        error_code = item.get("errorCode")
                        pic_name = item.get("picName")
                        pic_path = item.get("picPath")

                        if error_code in ALLOWED_ERROR_CODES and result.upper() in ('PASS', 'NG'):
                            try:
                                cursor.execute("""
                                    INSERT INTO AOI_JSON_Log 
                                    (id, log_file_name, barcode, machine, result, error_flag, error_code, pic_name, pic_path, DateTime)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                """, entry_id, file, barcode, machine, result, error_flag, error_code, pic_name, pic_path, file_time)
                            except pyodbc.IntegrityError:
                                continue
        start_date+=timedelta(days=1)

    exec_end_time=datetime.now()
    cursor.execute("""
            UPDATE AOI_Config
            SET exe_start_time = ?, exe_end_time = ?
            WHERE id = (SELECT TOP 1 id FROM AOI_Config ORDER BY id DESC)
        """, exe_start_time, exec_end_time)
    
    conn.commit()
    cursor.close()
    conn.close()
    print("All new JSON log entries added to SQL Server.")

if __name__ == "__main__":
    while True:
        interval_seconds = get_interval_from_db()
        main(interval_seconds)
        print(f"[{datetime.now()}] Sleeping for {interval_seconds} seconds...")
        time.sleep(interval_seconds)
