#!/usr/bin/env python3

import os
import time
import datetime
import sys

# file paths — all stored in the same directory as the script
QUEUE_FILE = "job_queue.txt"
COMPLETED_FILE = "completed_jobs.txt"
LOG_FILE = "scheduler_log.txt"

# round robin time quantum in seconds
TIME_QUANTUM = 5


# -------------------------------------------------------
# logging helper
# -------------------------------------------------------

def write_log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")


# -------------------------------------------------------
# file helpers — storing jobs as pipe-separated lines.
# format: student_id|job_name|exec_time|priority
# -------------------------------------------------------

def load_queue():
    jobs = []
    if not os.path.exists(QUEUE_FILE):
        return jobs
    with open(QUEUE_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if line == "":
                continue
            parts = line.split("|")
            if len(parts) != 4:
                # skip malformed lines rather than crashing
                continue
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


def append_completed(job, scheduling_type):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(COMPLETED_FILE, "a") as f:
        f.write(f"{job['student_id']}|{job['job_name']}|{job['exec_time']}|{job['priority']}|{scheduling_type}|{timestamp}\n")


def load_completed():
    completed = []
    if not os.path.exists(COMPLETED_FILE):
        return completed
    with open(COMPLETED_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if line == "":
                continue
            parts = line.split("|")
            if len(parts) != 6:
                continue
            completed.append({
                "student_id": parts[0],
                "job_name": parts[1],
                "exec_time": parts[2],
                "priority": parts[3],
                "scheduling_type": parts[4],
                "completed_at": parts[5]
            })
    return completed


# -------------------------------------------------------
# menu option 1: view pending jobs
# -------------------------------------------------------

def view_pending_jobs():
    print("\n=== pending job queue ===")
    jobs = load_queue()
    if len(jobs) == 0:
        print("no jobs currently in the queue.")
    else:
        print(f"{'#':<4} {'student id':<15} {'job name':<20} {'exec time (s)':<15} {'priority':<10}")
        print("-" * 65)
        for i, job in enumerate(jobs):
            print(f"{i+1:<4} {job['student_id']:<15} {job['job_name']:<20} {job['exec_time']:<15} {job['priority']:<10}")
    print()


# -------------------------------------------------------
# menu option 2: submit a job
# -------------------------------------------------------

def submit_job():
    print("\n=== submit a job request ===")

    student_id = input("enter student id: ").strip()
    if student_id == "":
        print("student id cannot be empty.")
        return

    job_name = input("enter job name: ").strip()
    if job_name == "":
        print("job name cannot be empty.")
        return

    # get execution time — keep asking until we get a valid number
    while True:
        exec_time_str = input("estimated execution time (seconds): ").strip()
        if exec_time_str.isdigit() and int(exec_time_str) > 0:
            exec_time = int(exec_time_str)
            break
        print("please enter a valid positive integer.")

    # get priority between 1 and 10
    while True:
        priority_str = input("job priority (1-10, where 10 is highest): ").strip()
        if priority_str.isdigit():
            priority = int(priority_str)
            if 1 <= priority <= 10:
                break
        print("priority must be a whole number between 1 and 10.")

    job = {
        "student_id": student_id,
        "job_name": job_name,
        "exec_time": exec_time,
        "priority": priority
    }

    # load current queue, append, save back
    jobs = load_queue()
    jobs.append(job)
    save_queue(jobs)

    write_log(f"job submitted — student: {student_id}, job: {job_name}, exec_time: {exec_time}s, priority: {priority}")
    print(f"\njob '{job_name}' submitted successfully.")
    print()


# -------------------------------------------------------
# menu option 3: process queue with round robin
# -------------------------------------------------------

def process_round_robin():
    print("\n=== processing job queue — round robin scheduling ===")
    print(f"time quantum: {TIME_QUANTUM} seconds\n")

    jobs = load_queue()

    if len(jobs) == 0:
        print("no jobs in the queue to process.")
        return

    # we work with a copy of the queue so we can track remaining time per job.
    # remaining_time tracks how much execution time is left for each job.
    remaining_time = []
    for job in jobs:
        remaining_time.append(job["exec_time"])

    # we process until all remaining times are zero
    # this is a simple simulation — we're not actually running real processes
    completed_indices = []
    total_jobs = len(jobs)
    current_time = 0

    print(f"starting round robin — {total_jobs} job(s) to process...\n")

    # keep looping through until everything is done
    while True:
        all_done = all(t <= 0 for t in remaining_time)
        if all_done:
            break

        for i in range(total_jobs):
            if remaining_time[i] <= 0:
                # this job is already finished, skip it
                continue

            job = jobs[i]
            slice_time = min(TIME_QUANTUM, remaining_time[i])

            print(f"  running: {job['job_name']} (student: {job['student_id']}) — time slice: {slice_time}s")
            write_log(f"round robin — executing '{job['job_name']}' for student {job['student_id']}, slice: {slice_time}s, scheduling: round_robin")

            # simulate the job running — sleep so you can actually see it happening
            time.sleep(slice_time)
            remaining_time[i] -= slice_time
            current_time += slice_time

            if remaining_time[i] <= 0:
                print(f"  completed: {job['job_name']} at t={current_time}s")
                write_log(f"job completed — '{job['job_name']}' for student {job['student_id']}, scheduling: round_robin")
                append_completed(job, "round_robin")
                completed_indices.append(i)

    # remove completed jobs from the queue file
    # rebuild the list without the ones we've just processed
    remaining_jobs = []
    for i, job in enumerate(jobs):
        if i not in completed_indices:
            remaining_jobs.append(job)

    save_queue(remaining_jobs)

    print(f"\nround robin complete. {len(completed_indices)} job(s) processed.")
    print()


# -------------------------------------------------------
# menu option 4: view completed jobs
# -------------------------------------------------------

def view_completed_jobs():
    print("\n=== completed jobs ===")
    completed = load_completed()
    if len(completed) == 0:
        print("no completed jobs yet.")
    else:
        print(f"{'student id':<15} {'job name':<20} {'exec time':<12} {'priority':<10} {'type':<15} {'completed at':<20}")
        print("-" * 95)
        for job in completed:
            print(f"{job['student_id']:<15} {job['job_name']:<20} {job['exec_time']:<12} {job['priority']:<10} {job['scheduling_type']:<15} {job['completed_at']:<20}")
    print()


# -------------------------------------------------------
# menu option 5: exit with confirmation
# -------------------------------------------------------

def exit_system():
    print()
    confirm = input("are you sure you want to exit? (y/n): ").strip().lower()
    if confirm == "y":
        write_log("user exited the scheduler.")
        print("goodbye.")
        sys.exit(0)
    else:
        print("exit cancelled.")
    print()


# -------------------------------------------------------
# main menu loop
# -------------------------------------------------------

def main():
    # make sure the log file exists from the start
    if not os.path.exists(LOG_FILE):
        write_log("scheduler started — log file initialised.")

    while True:
        print("--------------------------------")
        print("  university hpc job scheduler              ")
        print("--------------------------------")
        print("  1. view pending jobs")
        print("  2. submit a job request")
        print("  3. process queue")
        print("  4. view completed jobs")
        print("  5. exit")
        print("--------------------------------")

        choice = input("select an option [1-5]: ").strip()

        if choice == "1":
            view_pending_jobs()
        elif choice == "2":
            submit_job()
        elif choice == "3":
            process_round_robin()
        elif choice == "4":
            view_completed_jobs()
        elif choice == "5":
            exit_system()
        else:
            print("invalid option — please enter a number between 1 and 5.\n")


if __name__ == "__main__":
    main()
