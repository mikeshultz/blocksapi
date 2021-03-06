""" Various utility functions """

def pg_varchar_to_hex(h):
    if h[:2] == "\\x":
        return "0x" + h[2:]
    return h

def has_to_pg_varchar(h):
    if h[:2] == "0x":
        return "\\x" + h[2:]
    return h

def results_hex_format(results, field):
    """ Update the results of list of RawlResults to fix a hash that was stored
        in postgres' weird way of storing hex as varchar
    """
    for i in range(0, len(results)):
        if hasattr(results[i], field):
            results[i][field] = pg_varchar_to_hex(results[i][field])
        i += 1
    return results
