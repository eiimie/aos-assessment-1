#!/usr/bin/env python3

import os
import time

QUEUE_FILE = "job_queue.txt"
TIME_QUANTUM = 5

def load_queue():
    jobs = []
    if not os.path.exists(QUEUE_FILE):
        return jobs
    with open(QUEUE_FILE, "r") as f:
        for line in f:
            parts = line.strip().split("|")
            if len(parts) == 4:
                jobs.append({
                    "student_id": parts[0],
                    "job_name": parts[1],
                    "exec_time": int(parts[2]),
                    "priority": int(parts[3])
                })
    return jobs

def save_queue(jobs):
    with open(QUEUE_FILE, "w") as f:
        for job in jobs:
            f.write(f"{job['student_id']}|{job['job_name']}|{job['exec_time']}|{job['priority']}\n")

def view_pending():
    jobs = load_queue()
    print("\n=== pending jobs ===")
    if not jobs:
        print("queue empty")
    else:
        for i, job in enumerate(jobs):
            print(f"{i+1}: {job['student_id']} - {job['job_name']} ({job['exec_time']}s, prio {job['priority']})")
    print()

def submit():
    print("\n=== submit job ===")
    student_id = input("student id: ").strip()
    job_name = input("job name: ").strip()
    exec_time = int(input("exec time (seconds): "))
    priority = int(input("priority (1-10): "))
    jobs = load_queue()
    jobs.append({
        "student_id": student_id,
        "job_name": job_name,
        "exec_time": exec_time,
        "priority": priority
    })
    save_queue(jobs)
    print("job added.\n")

def round_robin():
    print("\n=== round robin processing ===")
    jobs = load_queue()
    if not jobs:
        print("nothing to process.")
        return
    remaining = [job["exec_time"] for job in jobs]
    completed_indices = []
    total = len(jobs)
    current_time = 0

    print(f"starting round robin (quantum={TIME_QUANTUM}s)...\n")
    while True:
        all_done = all(r <= 0 for r in remaining)
        if all_done:
            break
        for i in range(total):
            if remaining[i] <= 0:
                continue
            job = jobs[i]
            slice_time = min(TIME_QUANTUM, remaining[i])
            print(f"  running {job['job_name']} ({job['student_id']}) for {slice_time}s")
            time.sleep(slice_time)
            remaining[i] -= slice_time
            current_time += slice_time
            if remaining[i] <= 0:
                print(f"    finished {job['job_name']} at t={current_time}s")
                completed_indices.append(i)

    # remove processed jobs
    new_queue = [jobs[i] for i in range(total) if i not in completed_indices]
    save_queue(new_queue)
    print(f"\nprocessed {len(completed_indices)} jobs.\n")

def main():
    while True:
        print("=== HPC Job Scheduler (v2) ===")
        print("1. view pending")
        print("2. submit")
        print("3. process (round robin)")
        print("4. exit")
        choice = input("choice: ").strip()
        if choice == "1":
            view_pending()
        elif choice == "2":
            submit()
        elif choice == "3":
            round_robin()
        elif choice == "4":
            print("goodbye")
            break
        else:
            print("invalid\n")

if __name__ == "__main__":
    main()
