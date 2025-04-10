import time
import threading
import json
import signal
import sys
from collections import defaultdict, deque
from sseclient import SSEClient

EVENT_STREAM_URL = "https://stream.wikimedia.org/v2/stream/revision-create"
EVENT_WINDOW = deque()


WINDOW_SIZE = 60  # Start with 1 minute window (Task 1)
task_mode = 1

def collect_events():
    
    print(f"Connecting to Wikipedia Event Stream API...")
    
    while True:
        try:
            client = SSEClient(EVENT_STREAM_URL)
            
            for event in client:
                if event.event == 'message':
                    try:
                        if event.data and event.data.strip():
                            data = json.loads(event.data)
                            data['timestamp'] = time.time()
                            EVENT_WINDOW.append(data)
                    except json.JSONDecodeError:
                        pass
                    except Exception as e:
                        print(f"Error processing event: {type(e).__name__}: {str(e)}")
                        
        except Exception as e:
            print(f"Stream connection error: {type(e).__name__}: {str(e)}")
            print("Reconnecting in 5 seconds...")
            time.sleep(5)

def generate_reports(events):
    
    domain_pages = defaultdict(set)
    user_edits = {}
    
    for event in events:
        domain = event.get('meta', {}).get('domain')
        page_title = event.get('page_title')
        performer = event.get('performer', {})
        
        
        if domain and page_title:
            domain_pages[domain].add(page_title)
        
        
        if domain == "en.wikipedia.org" and not performer.get('user_is_bot', True):
            user = performer.get('user_text')
            edit_count = performer.get('user_edit_count', 0)
            if user and edit_count > 0:
                user_edits[user] = max(user_edits.get(user, 0), edit_count)
    

    print("\n========== Domains Report ==========")
    print(f"Total number of Wikipedia Domains Updated: {len(domain_pages)}")
    for domain, pages in sorted(domain_pages.items(), key=lambda x: len(x[1]), reverse=True):
        page_word = "page" if len(pages) == 1 else "pages"
        print(f"{domain}: {len(pages)} {page_word} updated")
    

    print("\n========== Users Report ==========")
    print("Users who made changes to en.wikipedia.org")
    if not user_edits:
        print("No regular users made edits to en.wikipedia.org in this time period.")
    else:
        for user, count in sorted(user_edits.items(), key=lambda x: x[1], reverse=True):
            print(f"{user}: {count}")

def report_worker():
    
    global WINDOW_SIZE, task_mode
    
    start_time = time.time()
    last_report_time = start_time
    
    while True:
        now = time.time()
        
        if now - last_report_time >= 60:
            window_minutes = WINDOW_SIZE / 60
            
            print("\n" + "="*60)
            print(f"TASK {task_mode}: Report based on last {window_minutes:.0f} minute(s) of data")
            print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(now))}")
            
            cutoff_time = now - WINDOW_SIZE
            
            removed = 0
            while EVENT_WINDOW and EVENT_WINDOW[0]['timestamp'] < cutoff_time:
                EVENT_WINDOW.popleft()
                removed += 1
            
            print(f"Events in current window: {len(EVENT_WINDOW)}")
            print("="*60)
            
            generate_reports(list(EVENT_WINDOW))
            
            last_report_time = now
        
        time.sleep(1)  # Check every second but only report every minute

def switch_to_task2(signum, frame):
    """Signal handler to switch from Task 1 to Task 2."""
    global WINDOW_SIZE, task_mode
    if task_mode == 1:
        WINDOW_SIZE = 300  # 5 minutes in seconds
        task_mode = 2
        print("\n" + "="*60)
        print("Switching to Task 2: 5-minute window reports")
        print("="*60)
    else:
        print("\nExiting Wikipedia monitor...")
        sys.exit(0)

if __name__ == "__main__":

    signal.signal(signal.SIGINT, switch_to_task2) # Switch tasks 
    
    print("="*60)
    print("Wikipedia Event Stream Monitor")
    print("="*60)
    print("Starting Task 1: 1-minute window reports")
    print("Press Ctrl+C once to switch to Task 2 (5-minute window)")
    print("Press Ctrl+C twice to exit")
    
    collector_thread = threading.Thread(target=collect_events, daemon=True)
    collector_thread.start()
    
    report_worker()
