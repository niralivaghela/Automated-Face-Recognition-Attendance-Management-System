 
# ══════════════════════════════════════════════════════════
#  ✏️  YOUR TWILIO CONFIG
# ══════════════════════════════════════════════════════════
ACCOUNT_SID   = 'AC5a0adee7ffc5d4a8d664d4cdb9156b39'
AUTH_TOKEN    = 'eb954e38b4af88702ed9f0f1ff25e353'

# ✅ This is ALWAYS Twilio's sandbox number — do NOT change this
FROM_WHATSAPP = 'whatsapp:+14155238886'

ENABLED       = True   # Set False to run in demo/test mode
# ══════════════════════════════════════════════════════════


def _clean_phone(phone):
    """Convert any Indian phone format to +91XXXXXXXXXX"""
    if not phone:
        return None
    p = str(phone).strip()
    p = p.replace(' ', '').replace('-', '').replace('(', '').replace(')', '').replace('+', '')

    if p.startswith('91') and len(p) == 12:
        return '+' + p          # 919876543210 → +919876543210
    if len(p) == 10 and p.isdigit():
        return '+91' + p        # 9876543210   → +919876543210
    return '+' + p              # fallback


def notify_absent(student_name, student_id, class_name, parent_phone, date_str):
    """
    Send WhatsApp absent alert to parent.
    Called automatically when student is marked absent.
    Skips silently if no phone number saved for student.
    """
    # No phone saved → skip silently
    if not parent_phone:
        print(f"[NOTIFY] No phone for {student_name} — skipping")
        return False, "No phone number"

    # Demo mode — prints to console only
    if not ENABLED:
        print(f"[WHATSAPP DEMO] Would send alert for {student_name} to {parent_phone}")
        print(f"[WHATSAPP DEMO] Set ENABLED=True to send real messages")
        return True, "Demo mode"

    phone = _clean_phone(parent_phone)
    if not phone:
        return False, f"Invalid phone number: {parent_phone}"

    # Safety check — from and to must be different
    if phone == '+14155238886':
        return False, "Cannot send to Twilio's own sandbox number!"

    try:
        from twilio.rest import Client
    except ImportError:
        return False, "Twilio not installed!\nRun: pip install twilio"

    try:
        client = Client(ACCOUNT_SID, AUTH_TOKEN)

        message_body = (
            f"Attendance Alert\n"
            f"Dear Parent,\n\n"
            f"Your ward *{student_name}*\n"
            f"ID: {student_id} | Class: {class_name}\n\n"
            f"was marked *ABSENT* on {date_str}.\n\n"
            f"Please contact the college if needed.\n"
            f"- Vanita Vishram Women's University"
        )

        msg = client.messages.create(
            body=message_body,
            from_=FROM_WHATSAPP,
            to=f'whatsapp:{phone}'
        )

        print(f"[✅ WHATSAPP SENT] {msg.sid} -> {phone}")
        return True, f"WhatsApp sent to {phone}"

    except Exception as e:
        err = str(e)

        # Show clear friendly error based on Twilio error code
        if '20003' in err:
            friendly = (
                "❌ Wrong Twilio credentials!\n"
                "Check ACCOUNT_SID and AUTH_TOKEN in notification_service.py"
            )
        elif '63031' in err:
            friendly = (
                "❌ From and To are same number!\n"
                "Student phone cannot be same as Twilio sandbox number."
            )
        elif '63007' in err or 'not opted in' in err.lower():
            friendly = (
                f"❌ {phone} has NOT joined the WhatsApp sandbox!\n\n"
                f"Parent must do this ONCE:\n"
                f"1. Open WhatsApp\n"
                f"2. Send your join code to +14155238886\n"
                f"   (find code at console.twilio.com -> Messaging -> Try WhatsApp)"
            )
        elif '21608' in err or 'unverified' in err.lower():
            friendly = (
                f"❌ {phone} is not verified in your Twilio trial!\n\n"
                f"To verify:\n"
                f"Console -> Phone Numbers -> Verified Caller IDs -> Add number"
            )
        else:
            friendly = f"❌ WhatsApp Error: {err}"

        print(f"[WHATSAPP ERROR] {friendly}")
        return False, friendly