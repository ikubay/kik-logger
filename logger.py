import sqlite3
import glob
import os
import time
from datetime import datetime

skip_groups = True

try:
    db = max(glob.iglob('*.db'), key=os.path.getctime)
except Exception as e:
    print(e)
    print("Could not load kikDatabase db file. Exiting.")
    quit()

print("Found kikDatabase db file: " + db)

conn = sqlite3.connect(db)
c = conn.cursor()
try:
    c.execute("SELECT * FROM messagesTable")
    messages = c.fetchall()
except Exception as e:
    print(e)
    print("Could not load 'messagesTable' from kikDatabase db file. Exiting.")
    quit()

# Open all existing txt files, get date from final line and convert to epoch
existing_log_files = [log for log in glob.glob("*.txt") if "kiklog" in log]
existing_messages = {}
for existing_log in existing_log_files:
    content = open(existing_log, "r", encoding="utf-8")
    existing_messages[existing_log] = ["".join(filter(str.isalpha, line)) for line in content]

created_logs = []
written_messages = 0

for message in messages:
    if message[1]:
        message_text = message[1].replace("\n", "")
    elif message[11]:
        message_text = message[11].replace("\n", "")
    else:
        continue

    # "bin_id"s (usernames) appear as username_<some random characters>@talk.kik.com
    # This code will remove that extra data and leave us with the username only.
    username = message[9]
    if skip_groups and "groups" in username:
        continue
    remove_portion = "_" + username[username.rindex("_")+1:]
    username = username.replace(remove_portion, "")

    file_name = "kiklog_" + username + ".txt"
    file1 = open(file_name, "a", encoding="utf-8")

    # Create human-readable timestamp in your timezone from the message's millisecond epoch
    formatted_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(message[8]) / 1000))

    if message[4]:
        message_data = formatted_time + " - YOU: "
    else:
        message_data = formatted_time + " - " + username + ": "

    if (file_name not in created_logs and file_name not in existing_log_files):
        formatted_message = message_data + message_text
    else:
        formatted_message = "\n" + message_data + message_text
    if file_name not in created_logs:
        created_logs.append(file_name)

    if file_name in existing_messages:
        new_message_alpha = "".join(filter(str.isalpha, formatted_message))
        if new_message_alpha in existing_messages[file_name]:
            continue

    file1.write(formatted_message)
    written_messages += 1

print("Done! Wrote " + str(written_messages) + " new messages to logs.")