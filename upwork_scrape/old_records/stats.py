import matplotlib
matplotlib.use('Agg')  # Headless backend

import csv
import os
from collections import defaultdict
from datetime import datetime
import matplotlib.pyplot as plt

# Get script directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# File paths
input_file = os.path.join(script_dir, 'posted_jobs_01.csv')
output_csv = os.path.join(script_dir, 'daily_job_counts.csv')
output_graph_all = os.path.join(script_dir, 'job_posting_trends.png')
output_graph_yes = os.path.join(script_dir, 'yes_jobs_by_day.png')
output_graph_yes_maybe = os.path.join(script_dir, 'yes_maybe_by_day_hour.png')
output_graph_total_by_day = os.path.join(script_dir, 'all_jobs_by_day_hour.png')

# Data containers
daily_counts = defaultdict(int)
weekday_map = {}
hourly_sentiment_counts = {'Yes': defaultdict(int), 'No': defaultdict(int), 'Maybe': defaultdict(int)}
yes_by_day = {d: defaultdict(int) for d in ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']}
yes_maybe_by_day = {d: defaultdict(int) for d in yes_by_day}
all_jobs_by_day = {d: defaultdict(int) for d in yes_by_day}

# Read and parse CSV
with open(input_file, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        time_posted = row.get('Time Posted', '').strip()
        recommendation = row.get('AI Recommendation', '').strip()

        if time_posted:
            try:
                dt = datetime.strptime(time_posted, '%m/%d/%Y %I:%M%p')
                date_str = dt.strftime('%Y-%m-%d')
                weekday = dt.strftime('%a').lower()
                hour = dt.hour

                # Count daily and hourly stats
                daily_counts[date_str] += 1
                weekday_map[date_str] = weekday
                all_jobs_by_day[weekday][hour] += 1

                if recommendation in hourly_sentiment_counts:
                    hourly_sentiment_counts[recommendation][hour] += 1

                if recommendation == 'Yes':
                    yes_by_day[weekday][hour] += 1
                    yes_maybe_by_day[weekday][hour] += 1
                elif recommendation == 'Maybe':
                    yes_maybe_by_day[weekday][hour] += 1

            except Exception as e:
                print(f"Error parsing '{time_posted}': {e}")

# Save daily job counts CSV
with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Date', 'Day', 'Jobs Posted'])
    for date in sorted(daily_counts):
        writer.writerow([date, weekday_map[date], daily_counts[date]])

# Common x-axis formatting
hours = list(range(24))
hour_labels = [datetime.strptime(str(h), "%H").strftime("%I %p").lstrip("0") for h in hours]

# ----- Plot 1: All jobs by sentiment per hour -----
for label in ['Yes', 'No', 'Maybe']:
    y = [hourly_sentiment_counts[label].get(h, 0) for h in hours]
    plt.plot(hour_labels, y, label=label)

plt.xlabel('Hour of Day')
plt.ylabel('Number of Jobs Posted')
plt.title('Job Postings by Hour and AI Recommendation')
plt.xticks(rotation=45)
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig(output_graph_all)
plt.close()

# ----- Plot 2: Yes jobs by hour/day -----
for day, data in yes_by_day.items():
    y = [data.get(h, 0) for h in hours]
    plt.plot(hour_labels, y, label=day.title())

plt.xlabel('Hour of Day')
plt.ylabel('Number of "Yes" Jobs')
plt.title('"Yes" Jobs by Hour and Day of Week')
plt.xticks(rotation=45)
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig(output_graph_yes)
plt.close()

# ----- Plot 3: Yes + Maybe jobs by hour/day -----
for day, data in yes_maybe_by_day.items():
    y = [data.get(h, 0) for h in hours]
    plt.plot(hour_labels, y, label=day.title())

plt.xlabel('Hour of Day')
plt.ylabel('Number of "Yes" + "Maybe" Jobs')
plt.title('"Yes" + "Maybe" Jobs by Hour and Day of Week')
plt.xticks(rotation=45)
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig(output_graph_yes_maybe)
plt.close()

# ----- Plot 4: All jobs by hour/day -----
for day, data in all_jobs_by_day.items():
    y = [data.get(h, 0) for h in hours]
    plt.plot(hour_labels, y, label=day.title())

plt.xlabel('Hour of Day')
plt.ylabel('Total Jobs Posted')
plt.title('All Jobs by Hour and Day of Week')
plt.xticks(rotation=45)
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig(output_graph_total_by_day)
plt.close()

print("Done. All graphs and CSV saved.")