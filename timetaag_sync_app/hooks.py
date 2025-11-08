
scheduler_events = {
    "cron": {
        "*/10 * * * *": [
            "timetaag_sync_app.background.timetaag_sync.sync_timetaag_checkins"
        ]
    }
}
