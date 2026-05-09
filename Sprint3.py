"""
HEALTH DATA ANALYTICS SYSTEM - MILESTONE 5 & 6
Topic: Health Data Analytics System
"""

import json
import os
import time
import asyncio
import pandas as pd
from typing import List, Dict
import concurrent.futures
from collections import deque

# ====================== EXCEPTIONS ======================
class InvalidHealthDataError(Exception): pass
class PatientNotFoundError(Exception): pass

# ====================== PATIENT CLASS (OOP) ======================
class Patient:
    def __init__(self, patient_id: str, name: str, age: int, gender: str):
        self.patient_id = patient_id
        self.name = name
        self.age = age
        self.gender = gender
        self.records: List[Dict] = []      # List
        self.conditions: set = set()       # Set

    def add_record(self, record: Dict):
        if not all(k in record for k in ['date', 'blood_pressure', 'heart_rate', 'temperature']):
            raise InvalidHealthDataError("Missing required fields")
        if not (30 <= record.get('heart_rate', 0) <= 200):
            raise InvalidHealthDataError("Invalid heart rate")
        
        self.records.append(record)
        if record.get('condition'):
            self.conditions.add(record['condition'])

# ====================== FUNCTIONAL PIPELINE ======================
def clean_record(record: Dict) -> Dict:
    cleaned = record.copy()
    cleaned['date'] = pd.to_datetime(cleaned['date']).date()
    if isinstance(cleaned.get('blood_pressure'), str):
        cleaned['blood_pressure'] = tuple(map(int, cleaned['blood_pressure'].split('/')))
    return cleaned

def health_data_pipeline(records: List[Dict]) -> Dict:
    cleaned = list(map(clean_record, records))
    df = pd.DataFrame(cleaned)
    anomalies = [r for r in cleaned if r.get('heart_rate', 70) < 55 or r.get('heart_rate', 70) > 110]
    
    return {
        "total_records": len(records),
        "avg_heart_rate": round(float(df['heart_rate'].mean()), 1),
        "avg_temperature": round(float(df['temperature'].mean()), 1),
        "anomalies_detected": len(anomalies)
    }

# ====================== MILESTONE 5: CONCURRENCY ======================
class ConcurrentHealthSystem:
    def __init__(self):
        self.patients: Dict[str, Patient] = {}
        self.analysis_queue: deque = deque()

    def add_patient(self, patient: Patient):
        self.patients[patient.patient_id] = patient
        print(f"✓ Patient {patient.name} added.")

    def add_record(self, patient_id: str, record: Dict):
        if patient_id not in self.patients:
            raise PatientNotFoundError(f"Patient {patient_id} not found")
        self.patients[patient_id].add_record(record)
        self.analysis_queue.append(patient_id)

    def process_patient(self, patient):
        """Helper for concurrent execution"""
        time.sleep(0.05)  # Simulate work
        return health_data_pipeline(patient.records)

    def concurrent_threading(self):
        """Multithreading"""
        start = time.time()
        results = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            future_to_pid = {executor.submit(self.process_patient, p): pid 
                           for pid, p in self.patients.items()}
            for future in concurrent.futures.as_completed(future_to_pid):
                pid = future_to_pid[future]
                results[pid] = future.result()
        duration = time.time() - start
        return {"method": "Multithreading", "time_taken": round(duration, 4)}

    async def concurrent_asyncio(self):
        """Asynchronous Programming"""
        start = time.time()
        tasks = [asyncio.sleep(0.05, result=health_data_pipeline(p.records)) 
                for p in self.patients.values()]
        await asyncio.gather(*tasks)
        duration = time.time() - start
        return {"method": "AsyncIO", "time_taken": round(duration, 4)}

# ====================== MILESTONE 6: NOVEL FEATURE ======================
def calculate_health_risk_score(record: Dict) -> float:
    """Novel Improvement: Intelligent Risk Scoring"""
    hr = record.get('heart_rate', 70)
    temp = record.get('temperature', 37.0)
    risk = 0.4 * abs(hr - 72) + 2.5 * abs(temp - 37.0)
    return round(risk, 2)

# ====================== MAIN DEMO ======================
if __name__ == "__main__":
    print("="*80)
    print("HEALTH DATA ANALYTICS SYSTEM - MILESTONE 5 & 6")
    print("="*80)

    system = ConcurrentHealthSystem()

    # Same dataset as previous milestones
    p1 = Patient("P001", "John Doe", 45, "Male")
    p2 = Patient("P002", "Jane Smith", 32, "Female")

    system.add_patient(p1)
    system.add_patient(p2)

    records = [
        {"date": "2025-04-01", "blood_pressure": "120/80", "heart_rate": 76, "temperature": 36.8},
        {"date": "2025-04-02", "blood_pressure": "135/85", "heart_rate": 98, "temperature": 37.4},
        {"date": "2025-04-03", "blood_pressure": "110/70", "heart_rate": 48, "temperature": 34.9}
    ]

    print("\n--- Adding Health Records ---")
    for rec in records:
        system.add_record("P001", rec)
        system.add_record("P002", rec)

    print("\n" + "="*70)
    print("MILESTONE 5: CONCURRENCY & HIGH-PERFORMANCE")
    print("="*70)
    
    thread_result = system.concurrent_threading()
    print(f"1. Multithreading Time     : {thread_result['time_taken']} seconds")

    async_result = asyncio.run(system.concurrent_asyncio())
    print(f"2. Asynchronous (AsyncIO)  : {async_result['time_taken']} seconds")

    print("\n" + "="*70)
    print("MILESTONE 6: RESEARCH CONTRIBUTION & NOVEL FEATURE")
    print("="*70)
    
    print("Intelligent Health Risk Scoring:")
    for pid, patient in system.patients.items():
        print(f"\nPatient {pid} - {patient.name}:")
        for i, rec in enumerate(patient.records):
            risk = calculate_health_risk_score(rec)
            print(f"   Record {i+1} → Risk Score: {risk}")

    print("\n" + "="*80)
    print("✅ MILESTONE 5 & 6 SUCCESSFULLY COMPLETED")
    print("="*80)