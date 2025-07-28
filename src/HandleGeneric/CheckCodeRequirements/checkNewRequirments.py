def compare_requirements(current_reqs, new_reqs):
    added = {}
    modified = {}

    for req_id, desc in new_reqs.items():
        if req_id not in current_reqs:
            added[req_id] = desc
        elif current_reqs[req_id] != desc:
            modified[req_id] = desc

    return {"added": added, "modified": modified}
