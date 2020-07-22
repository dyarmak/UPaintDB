from datetime import datetime

def check_status_change(proj, orig_status):
    # Check if the project status has been changed
    if orig_status != proj.status_id:
        # Check if status is now PaintingComplete(4) or Invoiced(5).
        if proj.status_id in (4,5):
            # and make sure that the status isn't changing from 4 to 5
            if orig_status != 4:
                # set date_finished only if it was changed from an active(1,2,3) to a finished state (4,5).
                proj.date_finished = datetime.now().date()

                # update the room table
                for rm in proj.room_list:
                    rm.date_last_paint = proj.date_finished