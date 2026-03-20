#!/usr/bin/env python3
# very basic job queue — just a list in memory.

import sys

jobs = []  # each job is a dict: student_id, job_name, exec_time, priority

def view_pending():
    print("\n=== pending jobs ===")
    if not jobs:
        print("no jobs.")
    else:
        for i, job in enumerate(jobs):
            print(f"{i+1}: {job['student_id']} - {job['job_name']} ({job['exec_time']}s, prio {job['priority']})")
    print()

def submit():
    print("\n=== submit a job ===")
    student_id = input("student id: ").strip()
    job_name = input("job name: ").strip()
    exec_time = int(input("exec time (seconds): "))
    priority = int(input("priority (1-10): "))
    jobs.append({
        "student_id": student_id,
        "job_name": job_name,
        "exec_time": exec_time,
        "priority": priority
    })
    print("job added.\n")

def main():
    while True:
        print("=== HPC Job Scheduler (v1) ===")
        print("1. view pending")
        print("2. submit")
        print("3. exit")
        choice = input("choice: ").strip()
        if choice == "1":
            view_pending()
        elif choice == "2":
            submit()
        elif choice == "3":
            print("goodbye")
            sys.exit(0)
        else:
            print("invalid\n")

if __name__ == "__main__":
    main()