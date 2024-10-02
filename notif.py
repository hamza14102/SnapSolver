from pync import Notifier

# # Customize your notification
# title = "Notification Title"
# message = "This is the notification message."

# # Send the notification
# Notifier.notify(message, title=title)


def notify(title, message):
    Notifier.notify(message, title=title)


# notify("Notification Title", "This is the notification message.")
