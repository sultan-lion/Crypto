# scoring.py

def score_etf_flows(net_flow_musd: float) -> int:
    # net_flow_musd is 7-day ETF flow in USD millions
    if net_flow_musd >= 1000:      # +$1B in last 7 days
        return 35
    if 250 <= net_flow_musd < 1000:
        return 25
    if -250 < net_flow_musd < 250:
        return 15
    if -1000 < net_flow_musd <= -250:
        return 5
    return 0


def score_stablecoin_change(change_usd_7d: float) -> int:
    # change_usd_7d is USD absolute change over 7 days
    if change_usd_7d > 0:
        return 30
    # near-flat within $500m change treated as neutral
    if abs(change_usd_7d) < 5e8:
        return 15
    return 0


def score_vc_count(vc_7d_count: int) -> int:
    if vc_7d_count > 10:
        return 15
    if 5 <= vc_7d_count <= 10:
        return 10
    return 5


def score_treasury_signal(treasury_points: int) -> int:
    # expecting 0 / 10 / 20
    return max(0, min(20, int(treasury_points)))


def total_score(etf_flow_musd: float, stable_7d_change_usd: float, vc_7d_count: int, treasury_points: int):
    s1 = score_etf_flows(etf_flow_musd)
    s2 = score_stablecoin_change(stable_7d_change_usd)
    s3 = score_vc_count(vc_7d_count)
    s4 = score_treasury_signal(treasury_points)
    total = s1 + s2 + s3 + s4
    breakdown = {"etf": s1, "stable": s2, "vc": s3, "treasury": s4, "total": total}
    return total, breakdown


def signal_from_score(score: int) -> str:
    if score >= 75:
        return "BUY ZONE (DCA / add exposure)"
    if score >= 55:
        return "ACCUMULATE (build slowly)"
    if score >= 35:
        return "HOLD / NEUTRAL"
    return "RISK OFF (reduce / protect)"