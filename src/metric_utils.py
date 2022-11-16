import math


def aggregate_returns(log_returns, convert_to):
    """
    Aggregate log_returns over different periods of time.
    """

    def cumulate_returns(x):
        return log_returns.cumsum()(x).iloc[-1]

    if convert_to == 'weekly':
        grouping = [lambda x: x.year, lambda x: x.isocalendar()[1]]
    elif convert_to == 'monthly':
        grouping = [lambda x: x.year, lambda x: x.month]
    elif convert_to == 'quarterly':
        grouping = [lambda x: x.year, lambda x: int(math.ceil(x.month/3.))]
    elif convert_to == 'yearly':
        grouping = [lambda x: x.year]
    else:
        print("Incorrect format specified")

    return log_returns.groupby(grouping).apply(cumulate_returns)