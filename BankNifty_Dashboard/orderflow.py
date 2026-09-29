def get_signal(price_change, oi_change):

    if price_change > 0 and oi_change > 0:
        return "LONG BUILDUP"

    if price_change < 0 and oi_change > 0:
        return "SHORT BUILDUP"

    if price_change > 0 and oi_change < 0:
        return "SHORT COVERING"

    if price_change < 0 and oi_change < 0:
        return "LONG UNWINDING"

    return "NEUTRAL"


def calculate_pcr(put_oi, call_oi):

    if call_oi == 0:
        return 0

    return put_oi / call_oi