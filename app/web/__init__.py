
def prepare_notification(show: bool, notification_type: str, notification_content: str) -> dict:

    extended_context: dict = {
            "notification": show,
            "notification_type": notification_type,
            "notification_content": notification_content
            }

    return extended_context
