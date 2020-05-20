def previous_2mo_high(ticker) -> int:
    high = ticker.history("2d").iloc[0]['High']
    for i in range(0, len(ticker.history("2mo")) - 2):
        temp_high = ticker.history("2mo").iloc[i]['High']
        if temp_high > high:
            high = temp_high
    return high
