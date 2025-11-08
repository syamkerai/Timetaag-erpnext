import frappe
from frappe.utils import now_datetime, add_minutes, datetime_to_timestamp, get_datetime

def sync_timetaag_checkins():
    API_KEY = "10249-1762594732-5UQ7G0IHJVJ4OQJ"
    BEARER_TOKEN = "YOUR_BEARER_TOKEN"
    API_URL = "https://app.timetaag.com/api/v1/GetDeviceLogs"
    DEFAULT_LAT = "-1.336908"
    DEFAULT_LONG = "36.882778"

    now = now_datetime()
    from_ts = int(datetime_to_timestamp(add_minutes(now, -10)))
    to_ts = int(datetime_to_timestamp(now))

    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "BioTaag-API-Key": API_KEY
    }

    payload = {
        "from_date": str(from_ts),
        "to_date": str(to_ts)
    }

    try:
        import requests
        res = requests.post(API_URL, headers=headers, json=payload)
        data = res.json()
        logs = data.get("data", [])

        created = 0

        for log in logs:
            device_id = log.get("UserId")
            timestamp_str = log.get("PunchDateTime")
            log_type = "IN" if log.get("SwipeDirection") == "1" else "OUT"
            lat = str(log.get("Lattitude") or DEFAULT_LAT)
            lon = str(log.get("Longitude") or DEFAULT_LONG)

            if not device_id or not timestamp_str:
                continue

            employee = frappe.db.get_value("Employee", {"attendance_device_id": device_id}, "name")
            if not employee:
                continue

            timestamp = get_datetime(timestamp_str)

            try:
                doc = frappe.new_doc("Employee Checkin")
                doc.employee = employee
                doc.time = timestamp
                doc.device_id = device_id
                doc.log_type = log_type
                doc.latitude = lat
                doc.longitude = lon
                doc.skip_auto_attendance = 0
                doc.insert(ignore_permissions=True)
                frappe.db.commit()
                created += 1
            except Exception as e:
                frappe.log_error(str(e), "Checkin Insert Error")

        frappe.log_error("TimeTagg Sync Summary", f"✅ Created: {created}")

    except Exception as e:
        frappe.log_error(str(e), "TimeTagg API Sync Failed")
