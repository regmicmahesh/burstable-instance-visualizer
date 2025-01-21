def calculate_earned_credit(
    *,
    baseline: float,
    vcpu_count: int,
    milliseconds: int = 1,
) -> float:
    return baseline * vcpu_count * (milliseconds / (60 * 1000))


def calculate_spent_credit(
    *,
    baseline: float,
    vcpu_count: int,
    utilization: float,
    milliseconds: int = 1,
) -> float:
    if utilization <= baseline:
        return 0.0

    credit_usage = utilization - baseline

    return credit_usage * vcpu_count * (milliseconds / (60 * 1000))


def calculate_max_credit(
    *,
    baseline: float,
    vcpu_count: int,
) -> float:
    return calculate_earned_credit(
        baseline=baseline,
        vcpu_count=vcpu_count,
        milliseconds=1000 * 60 * 60 * 24,
    )
